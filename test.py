import sys
try:
    from ddgs import DDGS
    print("Library 'ddgs' found!")
except ImportError:
    print("Library 'ddgs' NOT found. Install it with: pip install ddgs")
    sys.exit(1)

def run_test():
    print("Connecting to DuckDuckGo...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text("AI research 2026", max_results=3))
            if results:
                print(f"Success! Found {len(results)} results.")
                for r in results:
                    print(f"- {r.get('title')}")
            else:
                print("Connected, but 0 results found.")
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    run_test()