import argparse
import pickle
from pathlib import Path
import tqdm

from ddoautogear.item import Item

def main() -> None:
    # take in a path to an xml file
    parser = argparse.ArgumentParser()
    parser.add_argument('xml_path', type=Path)

    args = parser.parse_args()

    all_items: list[Item] = []

    if Path(args.xml_path).is_dir():
        for xml_file in tqdm.tqdm(Path(args.xml_path).iterdir()):
            try:
                item = Item.load_from_xml(xml_file)
                all_items.append(item)
            except Exception as e:
                print(f"Failed on {xml_file}")
                raise e
    else:
        item = Item.load_from_xml(args.xml_path)
        print(item)

    # pickle the all_items list:
    with open('all_items.pickle', 'wb') as f:
        pickle.dump(all_items, f)

if __name__ == "__main__":
    main()
