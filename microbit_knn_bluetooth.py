import asyncio
import threading
import numpy as np
from bleak import BleakClient, BleakScanner
import sys
import time
import os
import pickle
from sklearn.preprocessing import StandardScaler

MODEL_PATH = "knn_gesture_model.pkl"

UART_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
UART_RX_UUID      = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UART_TX_UUID      = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

WINDOW_SIZE      = 50 
MIN_BUFFER_READY = 10 


def extract_features(buffer: list) -> np.ndarray:
    window = np.array(buffer)
    features = []
    for axis in range(3):
        col = window[:, axis]
        features.append(np.mean(col))
        features.append(np.std(col))
        features.append(np.min(col))
        features.append(np.max(col))
        features.append(np.max(col) - np.min(col))
    return np.array(features)  # 15 fitur


class _BleSerAdapter:
    def __init__(self, send_bytes_threadsafe, is_open_fn):
        self._send    = send_bytes_threadsafe
        self._is_open = is_open_fn

    @property
    def is_open(self):
        try:
            return bool(self._is_open())
        except:
            return False

    def write(self, data: bytes):
        if data:
            self._send(data)

    def flush(self):
        pass


class MicrobitKNNBluetooth:
    def __init__(self, game=None, device_name_hint="micro:bit"):
        self.game             = game
        self.device_name_hint = device_name_hint.lower()

        # ── BLE ──────────────────────────────────────────────────────────
        self.ADDRESS   = "D8:A0:FA:21:8F:84"
        self.client    = None
        self.rx_uuid   = None
        self.tx_uuid   = None
        self.running   = True
        self.connected = False
        self._rx_buf   = ""

        self._send_lock        = threading.Lock()
        self._last_send_time   = 0
        self._min_send_interval= 0.05

        self.ser = _BleSerAdapter(self._send_bytes_threadsafe, lambda: self.connected)

        # ── KNN MODEL ────────────────────────────────────────────────────
        print("LOADING KNN MODEL...")
        try:
            with open(MODEL_PATH, "rb") as f:
                model_data = pickle.load(f)

            self.knn_model        = model_data["model"]
            self.label_map        = model_data["label_map"]
            self.scaler           = model_data["scaler"]
            self.reverse_label_map= {v: k for k, v in self.label_map.items()}

            print(f"✅ Model KNN loaded!")
            print(f"   K = {model_data.get('k', '?')} | Labels: {self.label_map}")

        except FileNotFoundError:
            print(f"❌ '{MODEL_PATH}' tidak ditemukan — jalankan training dulu")
            self.knn_model = self.scaler = None
            self.reverse_label_map = {}
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.knn_model = self.scaler = None
            self.reverse_label_map = {}

        # ── GAME STATE ───────────────────────────────────────────────────
        self.game_state          = "IDLE"
        self.spawned_count       = 0
        self.total_animals       = 0
        self.current_question_num= 0

        # ── GESTURE DETECTION ────────────────────────────────────────────
        self.gesture_buffer      = []
        self.buffer_size         = WINDOW_SIZE
        self.current_answer_idx  = None
        self.is_detecting        = False
        self.last_gesture_name   = None
        self.gesture_stable_count= 0
        self.current_gesture     = "─"
        self.confidence          = 0.0

        self.question_history    = []

        self._loop   = None
        self._thread = None


    # DISPLAY
    def print_status(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║     🎮 GAME NUMERASI DENGAN MICRO:BIT                           ║")
        print("╚══════════════════════════════════════════════════════════════════╝")

        if self.knn_model:
            print(f" 🤖 MODEL: KNN (K={self.knn_model.n_neighbors}) | Scaler: {'✓' if self.scaler else '✗'}")
        else:
            print(f" ⚠️  MODEL: TIDAK TERDETEKSI — menggunakan rule-based fallback")

        if self.connected:
            print(f" ✅ TERHUBUNG | State: {self.game_state}")
            print(f" 📍 Alamat: {self.ADDRESS}")
        else:
            print(" ⏳ Menghubungkan ke micro:bit...")

        print("══════════════════════════════════════════════════════════════════")

        if self.question_history:
            print("\n📚 HISTORY SOAL:")
            for entry in self.question_history:
                print(f"\n{'─' * 66}")
                icon = "✅" if entry['status'] == "SELESAI" else "⏳"
                print(f" {icon} Soal {entry['num']} | Spawn: {entry['spawned']}/{entry['total']} | {entry['status']}")
                for line in entry.get('lines', []):
                    print(f"   📝 {line[:60]}")

        print(f"\n{'═' * 66}")

        if self.game_state == "SPAWNING":
            print(f"\n📖 SOAL {self.current_question_num}")
            print(f" 🎲 Progress Spawn: {self.spawned_count}/{self.total_animals}")
            if self.total_animals > 0:
                p   = self.spawned_count / self.total_animals
                bar = "█" * int(p * 40) + "░" * (40 - int(p * 40))
                print(f" [{bar}] {p:.0%}")
            print("\n 💡 Goyang micro:bit untuk spawn hewan")

        elif self.game_state == "DETECTING":
            print(f"\n📖 SOAL {self.current_question_num}")
            print(f" 🎯 MEMILIH JAWABAN")

            gmap = {"tilt_left": "◀ KIRI", "up": "▲ ATAS", "tilt_right": "▶ KANAN", "─": "─ ─ ─"}
            print(f"\n 📍 Gesture: {gmap.get(self.current_gesture, self.current_gesture)}")
            bar = "█" * int(self.confidence * 40) + "░" * (40 - int(self.confidence * 40))
            print(f" 📊 Confidence: [{bar}] {self.confidence:.0%}")

            buf_filled = len(self.gesture_buffer)
            buf_min    = MIN_BUFFER_READY
            buf_bar    = "▉" * min(buf_filled, buf_min) + "░" * max(buf_min - buf_filled, 0)
            ready_str  = "✓ SIAP" if buf_filled >= buf_min else f"mengisi {buf_filled}/{buf_min}"
            print(f" 🔄 Buffer: [{buf_bar}] {ready_str}")

            if self.current_answer_idx is not None:
                labels = ["KIRI (0)", "ATAS (1)", "KANAN (2)"]
                print(f"\n ✓ Pilihan: {labels[self.current_answer_idx]}")
            else:
                print(f"\n ⚠  Belum ada gesture (buffer belum penuh atau gerak terlalu pelan)")

            print(f"\n 💡 ← Miring KIRI | ↑ Tegak ATAS | → Miring KANAN")
            print(f"    Tekan B untuk submit | Tekan A untuk restart deteksi")

        elif self.game_state == "READY":
            print(f"\n📖 SOAL {self.current_question_num}")
            print(" ✅ Spawn selesai! Tekan A di micro:bit untuk mulai deteksi.")

        print(f"\n{'═' * 66}\n")

    # CONNECTION
    def start(self):
        self._thread = threading.Thread(target=self._run_ble_thread, daemon=True)
        self._thread.start()
        print("🎮 Micro:bit BLE Controller dimulai...")
        time.sleep(1)

    def close(self):
        self.running = False
        if self.connected and self.client:
            try:
                asyncio.run_coroutine_threadsafe(self.client.disconnect(), self._loop)
            except:
                pass

    def _run_ble_thread(self):
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._ble_main())
        except Exception as e:
            print(f"❌ BLE error: {e}")
        finally:
            try:
                self._loop.close()
            except:
                pass

    #koneksi BLE
    async def _ble_main(self):
        print(f"🔗 Menghubungkan ke micro:bit ({self.ADDRESS})...")
        while self.running:
            try:
                async with BleakClient(self.ADDRESS, timeout=15.0) as client:
                    self.client    = client
                    self.connected = True
                    print("✅ Terhubung ke micro:bit!")
                    self.print_status()
                    await self._setup_uart(client)
                    while self.running and client.is_connected:
                        await asyncio.sleep(0.1)
            except Exception as e:
                self.connected = False
                self.client    = None
                if self.running:
                    print(f"⚠️  Koneksi terputus: {e}")
                    print("   Mencoba lagi dalam 3 detik...")
                    await asyncio.sleep(3)

    async def _setup_uart(self, client):
        try:
            await asyncio.sleep(1)

            uart_service = None
            for service in client.services:
                if service.uuid.lower() == UART_SERVICE_UUID.lower():
                    uart_service = service
                    break

            if not uart_service:
                print("❌ UART service tidak ditemukan!")
                return False

            self.rx_uuid = None
            self.tx_uuid = None

            for char in uart_service.characteristics:
                uuid = char.uuid.lower()
                if uuid == "6e400003-b5a3-f393-e0a9-e50e24dcca9e":
                    if "write" in char.properties:
                        self.rx_uuid = char.uuid
                elif uuid == "6e400002-b5a3-f393-e0a9-e50e24dcca9e":
                    if "indicate" in char.properties or "notify" in char.properties:
                        self.tx_uuid = char.uuid

            if not self.rx_uuid or not self.tx_uuid:
                print("⚠️  Characteristics tidak lengkap")
                return False

            await client.start_notify(self.tx_uuid, self._on_notify)
            await self._send_bytes(b"PING\n")
            return True

        except Exception as e:
            print(f"❌ Setup UART error: {e}")
            return False

    # DATA COMMUNICATION
    def _on_notify(self, _sender, data: bytearray):
        try:
            text = data.decode('utf-8', errors='ignore')
            self._process_received_data(text)
        except:
            pass

    def _process_received_data(self, data: str):
        self._rx_buf += data
        while '\n' in self._rx_buf or '\r' in self._rx_buf:
            sep = '\n' if '\n' in self._rx_buf else '\r'
            idx  = self._rx_buf.find(sep)
            line = self._rx_buf[:idx].strip()
            self._rx_buf = self._rx_buf[idx + 1:]
            if line:
                self._process_single_line(line)

    def _process_single_line(self, line: str):
        if line == "SHAKE":
            self._handle_shake()
        elif line == "A":
            self._handle_button_a()
        elif line == "B":
            self._handle_button_b()
        elif "," in line and line.count(",") == 2:
            self._handle_accel_data(line)
        elif line in ["READY", "RESET_OK", "PONG"]:
            pass

    # EVENT HANDLERS
    def _handle_shake(self):
        if self.game_state != "SPAWNING":
            print(f"⚠️  Shake diabaikan (state: {self.game_state})")
            return
        if not self.game:
            return

        before = getattr(self.game, "spawned_total", 0)
        try:
            self.game.on_shake()
        except Exception as e:
            print(f"⚠️ Error in game.on_shake: {e}")
            return

        after = getattr(self.game, "spawned_total", 0)
        if after <= before:
            return

        self.spawned_count = after
        self._send_bytes_threadsafe(f"SHOW:{self.spawned_count}\n".encode())
        time.sleep(0.05)
        self._send_bytes_threadsafe(b"SHAKE_OK\n")
        self.print_status()

        if self.total_animals > 0 and self.spawned_count >= self.total_animals:
            self.game_state = "READY"
            self._update_last_history("SPAWN SELESAI")
            print("🎯 Spawn selesai → READY")
            self.print_status()

    def _handle_button_a(self):
        print(f"\n🔘 Tombol A ditekan (state: {self.game_state})")
        if self.game_state in ("READY", "DETECTING"):
            self._start_detection()
            self._send_bytes_threadsafe(b"A_OK\n")
        else:
            print(f"⚠️  Tombol A diabaikan — state bukan READY/DETECTING")
            self._send_bytes_threadsafe(b"NOT_READY\n")

    def _handle_button_b(self):
        print(f"\n🔘 Tombol B ditekan (state: {self.game_state})")
        if self.game_state == "DETECTING":
            self._submit_answer()
            self._send_bytes_threadsafe(b"B_OK\n")
        else:
            print(f"⚠️  Tombol B diabaikan — state bukan DETECTING")

    def _handle_accel_data(self, line: str):
        if self.game_state != "DETECTING":
            return
        try:
            parts = line.split(",")
            if len(parts) != 3:
                return

            x, y, z = float(parts[0]), float(parts[1]), float(parts[2])

            self.gesture_buffer.append((x, y, z))
            if len(self.gesture_buffer) > self.buffer_size:
                self.gesture_buffer.pop(0)

            if len(self.gesture_buffer) < MIN_BUFFER_READY:
                print(f"  Buffer mengisi: {len(self.gesture_buffer)}/{MIN_BUFFER_READY} (min)")
                return

            t0 = time.perf_counter()

            if self.knn_model and self.scaler:
                idx, name, confidence = self._predict_with_knn()
            else:
                idx, name, confidence = self._predict_with_rules(x, y, z)

            print(f"[LATENCY] KNN inference: {(time.perf_counter()-t0)*1000:.2f} ms")

            if idx is not None:
                self.current_answer_idx   = idx
                self.current_gesture      = name
                self.confidence           = min(confidence, 1.0)

                if name == self.last_gesture_name:
                    self.gesture_stable_count += 1
                else:
                    self.gesture_stable_count = 1
                    self.last_gesture_name    = name

                if self.gesture_stable_count >= 3:
                    self._send_gesture_feedback(name)
                    self.gesture_stable_count = 0

            self.print_status()

        except Exception as e:
            print(f"⚠️  Error processing accel data: {e}")

    # GESTURE RECOGNITION — KNN
    def _predict_with_knn(self):
        try:
            buf = list(self.gesture_buffer)
            if not buf:
                return None, None, 0.0

            if len(buf) < WINDOW_SIZE:
                pad = [buf[0]] * (WINDOW_SIZE - len(buf))
                buf = pad + buf

            # Ekstrak 15 fitur statistik dari window data
            window_data     = buf[-WINDOW_SIZE:]  
            features        = extract_features(window_data)
            features_scaled = self.scaler.transform(features.reshape(1, -1))

            prediction = self.knn_model.predict(features_scaled)[0]

            if hasattr(self.knn_model, 'predict_proba'):
                probs      = self.knn_model.predict_proba(features_scaled)[0]
                confidence = float(probs[prediction])
            else:
                distances, _ = self.knn_model.kneighbors(features_scaled)
                confidence   = float(min(1.0 / (distances[0][0] + 1e-6), 1.0))

            gesture_name = self.reverse_label_map.get(prediction, "unknown")
            gesture_to_idx = {"tilt_left": 0, "up": 1, "tilt_right": 2}
            answer_idx = gesture_to_idx.get(gesture_name)

            buf_info = f"{len(self.gesture_buffer)}/{WINDOW_SIZE}"
            print(f"  KNN → {gesture_name} (idx={answer_idx}, conf={confidence:.2%}, buf={buf_info})")
            return answer_idx, gesture_name, confidence

        except Exception as e:
            print(f"⚠️  KNN prediction error: {e}")
            return None, None, 0.0

    def _predict_with_rules(self, x, y, z):
        try:
            if y > 100:
                return 0, "tilt_left",  min(abs(y) / 200.0, 1.0)
            elif y < -100:
                return 2, "tilt_right", min(abs(y) / 200.0, 1.0)
            elif x < -110:
                return 1, "up",         min(abs(x) / 200.0, 1.0)
            return None, None, 0.0
        except:
            return None, None, 0.0

    def _send_gesture_feedback(self, gesture_name: str):
        feedback = {"tilt_left": "LEFT", "up": "UP", "tilt_right": "RIGHT"}.get(gesture_name)
        if feedback:
            self._send_bytes_threadsafe(f"GESTURE_{feedback}\n".encode())

    # GAME FLOW CONTROL
    def send_reset(self):
        if self.game and hasattr(self.game, 'question_index'):
            self.current_question_num = self.game.question_index + 1

        self.game_state    = "SPAWNING"
        self.spawned_count = 0
        self._reset_detection_state()

        self._send_bytes_threadsafe(b"RESET\n")
        time.sleep(0.2)

        if self.current_question_num > 0:
            self._save_question_to_history("DIMULAI")

        print(f"\n✅ Reset untuk Soal {self.current_question_num}")
        self.print_status()

    def send_ready_to_answer(self):
        self.game_state = "READY"
        self._update_last_history("SPAWN SELESAI")
        self._send_bytes_threadsafe(b"READY_TO_ANSWER\n")
        time.sleep(0.2)
        print(f"\n✅ Soal {self.current_question_num} — Siap pilih jawaban!")
        self.print_status()

    def send_correct_feedback(self):
        self._send_bytes_threadsafe(b"ANSWER_CORRECT\n")
        time.sleep(0.1)

    def send_wrong_feedback(self):
        self._send_bytes_threadsafe(b"ANSWER_WRONG\n")
        time.sleep(0.1)

    def _start_detection(self):
        print(f"\n🎯 Mulai deteksi gesture — Soal {self.current_question_num}")
        if self.knn_model:
            print(f"   Model: KNN (K={self.knn_model.n_neighbors}), window={WINDOW_SIZE}")
        else:
            print(f"   ⚠️  Rule-based fallback aktif")

        self.game_state           = "DETECTING"
        self.is_detecting         = True
        self.gesture_buffer       = []
        self.current_answer_idx   = None
        self.last_gesture_name    = None
        self.gesture_stable_count = 0
        self.current_gesture      = "─"
        self.confidence           = 0.0

        self._update_last_history("MEMILIH JAWABAN")
        self.print_status()
        self._send_bytes_threadsafe(b"DETECT_START\n")

    def _submit_answer(self):
        if self.current_answer_idx is None and len(self.gesture_buffer) >= MIN_BUFFER_READY:
            print("  ⚡ Memaksa prediksi dari buffer yang ada...")
            if self.knn_model and self.scaler:
                idx, name, conf = self._predict_with_knn()
            else:
                last = self.gesture_buffer[-1]
                idx, name, conf = self._predict_with_rules(*last)
            if idx is not None:
                self.current_answer_idx = idx
                self.current_gesture    = name
                self.confidence         = conf

        if self.current_answer_idx is None:
            print("\n⚠️  Tidak ada gesture terdeteksi!")
            print(f"   Buffer saat ini: {len(self.gesture_buffer)}/{MIN_BUFFER_READY} (min)")
            print("   Gerakkan micro:bit lebih lama lalu tekan A untuk restart")
            self._send_bytes_threadsafe(b"NO_GESTURE\n")
            return

        labels     = ["KIRI", "ATAS", "KANAN"]
        answer_txt = labels[self.current_answer_idx]

        print(f"\n{'═' * 66}")
        print(f"📤 SUBMIT JAWABAN: {answer_txt} (index {self.current_answer_idx})")
        print(f"   Confidence: {self.confidence:.2%}")
        print(f"{'═' * 66}")

        if hasattr(self.game, "on_microbit_answer"):
            try:
                self.game.on_microbit_answer(self.current_answer_idx)
                time.sleep(0.5)

                if self.game and hasattr(self.game, 'blocks'):
                    block = self.game.blocks[self.current_answer_idx]
                    if block.is_correct:
                        print(f"\n✅ JAWABAN BENAR! Skor: {self.game.score}")
                    else:
                        correct = next((b.text for b in self.game.blocks if b.is_correct), "?")
                        print(f"\n❌ JAWABAN SALAH! Benar: {correct}")
            except Exception as e:
                print(f"❌ Error saat submit: {e}")

        self._update_last_history("SELESAI")
        self._reset_detection_state()
        self.game_state = "IDLE"
        time.sleep(1)
        self.print_status()

    def _reset_detection_state(self):
        self.is_detecting         = False
        self.gesture_buffer       = []
        self.current_answer_idx   = None
        self.last_gesture_name    = None
        self.gesture_stable_count = 0
        self.current_gesture      = "─"
        self.confidence           = 0.0

    def _save_question_to_history(self, status):
        lines = []
        if self.game and hasattr(self.game, 'current_question') and self.game.current_question:
            lines = self.game.current_question.get('lines', [])[:2]

        entry = {
            'num':     self.current_question_num,
            'spawned': self.spawned_count,
            'total':   self.total_animals,
            'status':  status,
            'lines':   lines,
        }
        self.question_history.append(entry)
        if len(self.question_history) > 5:
            self.question_history.pop(0)

    def _update_last_history(self, status):
        if self.question_history:
            self.question_history[-1]['status']  = status
            self.question_history[-1]['spawned'] = self.spawned_count

    # 📤 BLE LOW
    def _send_bytes_threadsafe(self, data: bytes):
        if not data or not self._loop or not self.connected:
            return

        def _send():
            try:
                asyncio.run_coroutine_threadsafe(self._send_bytes(data), self._loop)
            except:
                pass

        threading.Thread(target=_send, daemon=True).start()

    async def _send_bytes(self, data: bytes):
        if not (self.client and self.client.is_connected and self.rx_uuid):
            return
        try:
            await self.client.write_gatt_char(self.rx_uuid, data, response=False)
        except Exception:
            pass