def build_chunk_tree(chunks):
    chunk_dict = {chunk.id: {"id": chunk.id, "content": chunk.content, "children": []} for chunk in chunks}
    root_nodes = []

    for chunk in chunks:
        node = chunk_dict[chunk.id]
        if chunk.parent_id:
            parent_node = chunk_dict.get(chunk.parent_id)
            if parent_node:
                parent_node["children"].append(node)
        else:
            root_nodes.append(node)

    return root_nodes
