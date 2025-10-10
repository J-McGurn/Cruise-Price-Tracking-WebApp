from price_trackers import po_price_tracker as po_tracker
from price_trackers import princess_price_tracker as princess_tracker

def main():
    print("\n▶ Running P&O tracker...")
    po_tracker.main()
    
    print("▶ Running Princess tracker...")
    princess_tracker.main()

    print("\n✅ All trackers finished!")

if __name__ == "__main__":
    main()