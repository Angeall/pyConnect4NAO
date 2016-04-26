__author__ = 'Anthony Rouneau'


class Node(object):
    def __init__(self, _data, _children=None):
        """
        :param _data: the data inside the node
        :param _children: the children of the node
        :type _children: list
        """
        if _children is None:
            _children = []
        self.data = _data
        self.children = _children

    def add_child(self, child):
        """
        :param child: the new child of the node
        """
        self.children.append(child)

    def get_child(self, index):
        """
        :param index: the index of the child to return
        :type index: int
        :return: the index th child
        """
        return self.children[index]

    def get_data(self):
        """
        :return: the data inside the node
        """
        return self.data


class Tree(object):
    def __init__(self, _root=None):
        """
        :param _root: the root of the tree
        :type _root: Node
        """
        self.root = _root

    def set_head(self, _root):
        """
        :param _root: the nes root of the tree
        :type _root: Node
        Replace the current root of the tree
        """
        self.root = _root
