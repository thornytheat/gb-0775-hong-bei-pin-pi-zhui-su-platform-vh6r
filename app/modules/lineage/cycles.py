from collections import deque


def finish_order(edges):
    seen, finished=set(),[]
    for root in sorted(edges):
        if root in seen:
            continue
        seen.add(root)
        stack=[(root,iter(sorted(edges[root])))]
        while stack:
            node,children=stack[-1]
            child=next(children,None)
            if child is None:
                finished.append(node)
                stack.pop()
            elif child not in seen:
                seen.add(child)
                stack.append((child,iter(sorted(edges[child]))))
    return finished


def witness(edges, component):
    start=min(component)
    paths=deque([(start,[start])])
    seen={start}
    while paths:
        node,path=paths.popleft()
        for child in sorted(edges[node] & component):
            if child==start:
                return [*path,start]
            if child not in seen:
                seen.add(child)
                paths.append((child,[*path,child]))
    raise RuntimeError('循环分量没有可复核路径')


def find_cycles(edges):
    reverse={node:set() for node in edges}
    for node, upstream in edges.items():
        for source in upstream:
            reverse[source].add(node)
    visited,result=set(),[]
    for root in reversed(finish_order(edges)):
        if root in visited:
            continue
        component,stack={root},[root]
        visited.add(root)
        while stack:
            additions=reverse[stack.pop()] - visited
            component.update(additions)
            visited.update(additions)
            stack.extend(additions)
        if len(component)>1 or root in edges[root]:
            result.append(dict(members=sorted(component),path=witness(edges,component)))
    return sorted(result,key=lambda row:row['members'])
