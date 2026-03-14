from datasets_loader import LOADERS

def test_all():
    failed = []
    for name, loader in LOADERS.items():
        if name == "math":
            continue
        try:
            print(f"Loading {name}...")
            # some datasets only have subset or validation splits
            # we'll just try 'test' or 'val'
            samples = loader(split="test" if name not in ["drop"] else "val", seed=42)
            print(f"  Success: {len(samples)} samples loaded for {name}")
        except Exception as e:
            print(f"  Error loading {name}: {e}")
            failed.append(name)
            
    print(f"\nFailed: {failed}")

if __name__ == "__main__":
    test_all()
