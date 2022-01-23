import pprint
from collections import defaultdict

def make_tree_dict(inputs):
    tree_dict = {}
    for i, ainput in enumerate(inputs):
        print(ainput)
        print(f'tree_dict:{tree_dict}')
        pre_dict = tree_dict
        for j, key in enumerate(ainput):
            if j == len(ainput)-2:
                pre_dict[key] = ainput[-1]
                break
            elif key not in pre_dict:
                pre_dict[key] = {} 
            else:
                pass 
            print(f'1:{pre_dict}')
            pre_dict = pre_dict[key]
            print(f'2:{pre_dict}')
    return tree_dict

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(width=10,compact=True)
    inputs = []
    with open("../data/example.csv") as f:
        for line in f:
            line = line.rstrip().split(",")
            inputs.append(line)
    print(inputs)
    hoge = make_tree_dict(inputs) 
    pp.pprint(hoge)

    recursive_defaultdict = lambda: defaultdict(recursive_defaultdict)
    hoge = recursive_defaultdict()
    hoge = inputs
    print(hoge)



