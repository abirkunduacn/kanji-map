function convertNode(node) {
  return {
    char: node.char,
    name: node.label,
    label: node.label,
    children: (node.children || []).map(convertNode),
  };
}

export function toHierarchy(root) {
  return {
    char: root.root,
    name: root.label,
    label: root.label,
    children: (root.children || []).map(convertNode),
  };
}

export function countNodes(h) {
  let n = 1;
  for (const c of h.children || []) n += countNodes(c);
  return n;
}
