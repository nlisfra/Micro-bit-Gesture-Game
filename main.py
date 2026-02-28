import sys
import os
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from math_game import MathGame
from microbit_knn_bluetooth import MicrobitKNNBluetooth


def main():
    print("=" * 60)
    print("   GAME MATEMATIKA CERITA - DENGAN MICRO:BIT GESTURE")
    print("=" * 60)
    print("\nMemulai game...")
    
    game = MathGame()
    
    print("\n🔗 Menginisialisasi koneksi micro:bit...")
    microbit = MicrobitKNNBluetooth(game=game)
    game.microbit = microbit 
    
    microbit.start()
    
    print("⏳ Menunggu koneksi micro:bit...")
    time.sleep(2)
    
    try:
        game.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Game dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🧹 Membersihkan resources...")
        microbit.close()
        print("👋 Sampai jumpa!")


if __name__ == "__main__":
    main()