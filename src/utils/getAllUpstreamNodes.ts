export function getAllUpstreamNodes(node: any, allNodes: any[], visited = new Set<number>()): any[] {
    const result: any[] = []
    for (const id of node.beforeWorkflowNodeIds) {
        if (visited.has(id)) continue // 避免重复或死循环
        visited.add(id)
        const upstreamNode = allNodes.find(n => n.id === id)
        if (upstreamNode) {
            result.push(upstreamNode)
            result.push(...getAllUpstreamNodes(upstreamNode, allNodes, visited))
        }
    }

    return result
}