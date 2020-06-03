from RenderStarter import Node, Event, ReconMap, EventType, Tree
### Host Tree

root = Node("root")
root.root = True
root.order = 0

internal1 = Node("internal") # parent of 4 and 5
internal1.is_leaf = False
internal1.parent = root
internal1.order = 2

leaf4 = Node("4")
leaf4.is_leaf = True
leaf4.parent = internal1
leaf4.order = 4

leaf5 = Node("5")
leaf5.is_leaf = True
leaf5.parent = internal1
leaf5.order = 4

leaf3 = Node("3")
leaf3.is_leaf = True
leaf3.parent = root
leaf3.order = 4

root.leftChild = internal1
root.rightChild = leaf3
internal1.leftChild = leaf4
internal1.rightChild = leaf5

hostTree = Tree()
hostTree.rootNode = root
hostTree.allNodes = [root, internal1, leaf4, leaf5, leaf3]
hostTree.type = 1
### Parasite Tree

pRoot = Node("pRoot")
pRoot.root = True
pRoot.order = 1

pInternal = Node("pInternal")
pInternal.is_leaf = False
pInternal.parent = pRoot
pInternal.order = 3

pLeaf7 = Node("7")
pLeaf7.is_leaf = True
pLeaf7.parent = pRoot
pLeaf7.order = 4

pLeaf9 = Node("9")
pLeaf9.is_leaf = True
pLeaf9.parent = pInternal
pLeaf9.order = 4

pLeaf10 = Node("10")
pLeaf10.is_leaf = True
pLeaf10.parent = pInternal
pLeaf10.order = 4

pRoot.leftChild = pLeaf7
pRoot.rightChild = pInternal
pInternal.leftChild = pLeaf9
pInternal.rightChild = pLeaf10

ParasiteTree = Tree()
ParasiteTree.rootNode = pRoot
ParasiteTree.allNodes = [pRoot, pInternal, pLeaf7, pLeaf9, pLeaf10]
ParasiteTree.type = 2

### Reconciliation

R = ReconMap()
Event1 = Event("7", "4", EventType.TIPTIP)
Event2 = Event("9", "5", EventType.TIPTIP)
Event3 = Event("10", "3", EventType.TIPTIP)
Event4 = Event("pInternal", "5", EventType.TRANSFER)



