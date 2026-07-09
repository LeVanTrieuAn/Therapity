(function () {
    // Build a tree from graphData (binary: max 2 children)
    function buildTree(graphData) {
        const nodes = graphData.nodes || [];
        const edges = graphData.edges || [];
        if (!nodes || nodes.length === 0) return null;

        // Root = node with no incoming edges
        const hasIncoming = new Set(edges.map(e => e.target));
        const rootNode = nodes.find(n => !hasIncoming.has(n.id)) || nodes[0];

        // Build child adjacency (N-ary tree)
        const childMap = {};
        nodes.forEach(n => { childMap[n.id] = []; });
        edges.forEach(e => {
            if (childMap[e.source]) {
                childMap[e.source].push({ id: e.target, edgeLabel: e.label, isContradiction: !!e.is_contradiction });
            }
        });

        const visited = new Set();
        const build = (id, depth = 0) => {
            if (visited.has(id) || depth > 12) return null;
            visited.add(id);
            const nd = nodes.find(n => n.id === id);
            if (!nd) return null;
            const children = (childMap[id] || []).map(({ id: cid, edgeLabel, isContradiction }) => {
                const child = build(cid, depth + 1);
                if (child) { child.edgeLabel = edgeLabel; child.isContradiction = isContradiction; }
                return child;
            }).filter(Boolean);
            return { ...nd, children, depth };
        };

        return build(rootNode.id);
    }

    window.renderBinaryTreeGraph = function (containerId, graphData, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const isInteractive = options.interactive !== false;

        container.innerHTML = '';
        const NS = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(NS, 'svg');
        svg.id = containerId + '-svg';
        svg.style.cssText = `width:100%;height:100%;display:block;${isInteractive ? 'cursor:grab;' : ''}`;

        // Glow filter
        const defs = document.createElementNS(NS, 'defs');
        defs.innerHTML = `<filter id="tree-glow" x="-60%" y="-60%" width="220%" height="220%"><feMerge><feMergeNode in="SourceGraphic"/></feMerge></filter>`;
        svg.appendChild(defs);

        const g = document.createElementNS(NS, 'g');
        g.id = containerId + '-g';
        svg.appendChild(g);
        container.appendChild(svg);

        let treeTransform = { x: 0, y: 0, scale: 1 };
        let isDraggingTree = false;
        let dragStartTree = { x: 0, y: 0 };

        let draggingNode = null;
        let nodeDragStart = { x: 0, y: 0 };
        let allEdges = [];
        let allNodes = [];

        const applyTransform = () => {
            g.setAttribute('transform', `translate(${treeTransform.x},${treeTransform.y}) scale(${treeTransform.scale})`);
        };

        const resolveCollisions = (nodes, draggingNode) => {
            const padX = 24; // horizontal spacing buffer
            const padY = 24; // vertical spacing buffer
            const iterations = 5;

            for (let it = 0; it < iterations; it++) {
                let collisionFound = false;
                for (let i = 0; i < nodes.length; i++) {
                    for (let j = i + 1; j < nodes.length; j++) {
                        const n1 = nodes[i];
                        const n2 = nodes[j];

                        const l1 = n1.x - n1.width/2, r1 = n1.x + n1.width/2, t1 = n1.y, b1 = n1.y + n1.height;
                        const l2 = n2.x - n2.width/2, r2 = n2.x + n2.width/2, t2 = n2.y, b2 = n2.y + n2.height;

                        const overlapX = Math.min(r1 + padX, r2 + padX) - Math.max(l1 - padX, l2 - padX);
                        const overlapY = Math.min(b1 + padY, b2 + padY) - Math.max(t1 - padY, t2 - padY);

                        if (overlapX > 0 && overlapY > 0) {
                            collisionFound = true;
                            if (overlapX < overlapY) {
                                const pushDist = overlapX;
                                const dir = n1.x < n2.x ? 1 : -1;
                                if (n1 === draggingNode) {
                                    n2.x += pushDist * dir;
                                } else if (n2 === draggingNode) {
                                    n1.x -= pushDist * dir;
                                } else {
                                    n1.x -= pushDist * dir * 0.5;
                                    n2.x += pushDist * dir * 0.5;
                                }
                            } else {
                                const pushDist = overlapY;
                                const dir = n1.y < n2.y ? 1 : -1;
                                if (n1 === draggingNode) {
                                    n2.y += pushDist * dir;
                                } else if (n2 === draggingNode) {
                                    n1.y -= pushDist * dir;
                                } else {
                                    n1.y -= pushDist * dir * 0.5;
                                    n2.y += pushDist * dir * 0.5;
                                }
                            }
                        }
                    }
                }
                if (!collisionFound) break;
            }
        };

        if (isInteractive) {
            svg.addEventListener('pointerdown', (e) => {
                if (e.button !== 0 || draggingNode) return;
                isDraggingTree = true;
                dragStartTree = { x: e.clientX - treeTransform.x, y: e.clientY - treeTransform.y };
                svg.style.cursor = 'grabbing';
                svg.setPointerCapture(e.pointerId);
                e.preventDefault();
            });

            svg.addEventListener('pointermove', (e) => {
                if (draggingNode) {
                    const dx = e.clientX - nodeDragStart.x;
                    const dy = e.clientY - nodeDragStart.y;
                    nodeDragStart = { x: e.clientX, y: e.clientY };

                    draggingNode.x += dx / treeTransform.scale;
                    draggingNode.y += dy / treeTransform.scale;

                    resolveCollisions(allNodes, draggingNode);

                    allNodes.forEach(node => {
                        node.element.setAttribute('transform', `translate(${node.x - node.width / 2},${node.y})`);
                    });

                    allEdges.forEach(edge => {
                        const x1 = edge.from.x, y1 = edge.from.y + edge.from.height;
                        const x2 = edge.to.x, y2 = edge.to.y;
                        const cy = (y1 + y2) / 2;

                        edge.pathElement.setAttribute('d', `M${x1},${y1} C${x1},${cy} ${x2},${cy} ${x2},${y2}`);
                        edge.arrowElement.setAttribute('points', `${x2},${y2} ${x2 - 5},${y2 - 10} ${x2 + 5},${y2 - 10}`);
                        if (edge.labelElement) {
                            const midX = (x1 + x2) / 2;
                            const offset = 12;
                            let textX, anchor;
                            if (x2 < x1) {
                                textX = midX - offset;
                                anchor = 'end';
                            } else {
                                textX = midX + offset;
                                anchor = 'start';
                            }
                            edge.labelElement.setAttribute('x', textX.toString());
                            edge.labelElement.setAttribute('y', (cy + 4).toString());
                            edge.labelElement.setAttribute('text-anchor', anchor);
                        }
                    });
                    return;
                }

                if (!isDraggingTree) return;
                treeTransform.x = e.clientX - dragStartTree.x;
                treeTransform.y = e.clientY - dragStartTree.y;
                applyTransform();
            });

            const stopDragging = (e) => {
                if (draggingNode) {
                    draggingNode.element.style.cursor = 'grab';
                    draggingNode = null;
                    svg.style.cursor = 'grab';
                    try { svg.releasePointerCapture(e.pointerId); } catch (err) { }
                    return;
                }
                if (!isDraggingTree) return;
                isDraggingTree = false;
                svg.style.cursor = 'grab';
                try { svg.releasePointerCapture(e.pointerId); } catch (err) { }
            };

            svg.addEventListener('pointerup', stopDragging);
            svg.addEventListener('pointercancel', stopDragging);

            svg.addEventListener('wheel', (e) => {
                e.preventDefault();
                const rect = svg.getBoundingClientRect();
                const mx = e.clientX - rect.left;
                const my = e.clientY - rect.top;
                const factor = e.deltaY > 0 ? 0.9 : 1.1;
                const newScale = Math.max(0.2, Math.min(4, treeTransform.scale * factor));
                treeTransform.x = mx - (mx - treeTransform.x) * (newScale / treeTransform.scale);
                treeTransform.y = my - (my - treeTransform.y) * (newScale / treeTransform.scale);
                treeTransform.scale = newScale;
                applyTransform();
            }, { passive: false });
        }

        const isLight = !document.documentElement.classList.contains('dark');
        const fontColor = isLight ? '#162061' : '#ffffff';
        const edgeColor = isLight ? 'rgba(22,32,97,0.38)' : '#5a5230';
        const mk = (tag) => document.createElementNS(NS, tag);

        const tree = buildTree(graphData);
        g.innerHTML = '';

        if (!tree) {
            const fo = mk('foreignObject');
            fo.setAttribute('x', '-140'); fo.setAttribute('y', '-35');
            fo.setAttribute('width', '280'); fo.setAttribute('height', '90');
            let emptyMessage = (window.t && window.t('coach.no_mindmap_data')) || '';
            fo.innerHTML = `<div id="${containerId}-empty-msg" xmlns="http://www.w3.org/1999/xhtml" style="text-align:center;color:${isLight ? '#94a3b8' : '#475569'};font-family:Inter,sans-serif;font-size:13px;line-height:1.9;padding:10px 8px">${emptyMessage}</div>`;
            g.appendChild(fo);

            treeTransform = { x: container.clientWidth / 2, y: container.clientHeight / 2, scale: 1 };
            applyTransform();
            return;
        }

        // Layout constants
        const HG = 30, VG = 104;

        const precalculate = (node) => {
            const raw = (node.label || '').trim();
            let lines = [];
            let currentStr = raw;
            const MAX_CHARS = 24;
            while(currentStr.length > 0) {
                if(currentStr.length <= MAX_CHARS) {
                    lines.push(currentStr);
                    break;
                }
                let sp = currentStr.lastIndexOf(' ', MAX_CHARS);
                if (sp <= 0) sp = currentStr.indexOf(' ');
                if (sp === -1) sp = MAX_CHARS;
                
                lines.push(currentStr.slice(0, sp));
                currentStr = currentStr.slice(sp).trim();
            }
            if (lines.length === 0) lines.push('');
            node.lines = lines;
            node.height = Math.max(60, 24 + lines.length * 16 + 14); 

            // Calculate dynamic width based on text length
            const maxLineLen = Math.max(...lines.map(l => l.length));
            node.width = Math.max(120, 57 + maxLineLen * 6.2 + 18); // 57px icon padding + 6.2px per char + 18px right padding
            
            (node.children || []).forEach(precalculate);
        };
        if (tree) precalculate(tree);

        // Subtree width calculation
        const calcW = (node) => {
            if (!node.children || node.children.length === 0) return node.width + HG;
            return Math.max(node.width + HG, node.children.reduce((s, c) => s + calcW(c), 0));
        };

        // Position assignment (centered)
        let minX = Infinity, maxX = -Infinity, maxY = -Infinity, maxBottom = -Infinity;
        const assign = (node, cx, y) => {
            node.x = cx; node.y = y;
            if (cx < minX) minX = cx;
            if (cx > maxX) maxX = cx;
            if (y > maxY) maxY = y;
            if (y + node.height > maxBottom) maxBottom = y + node.height;

            if (!node.children || node.children.length === 0) return;
            const total = node.children.reduce((s, c) => s + calcW(c), 0);
            let lx = cx - total / 2;
            node.children.forEach(child => {
                const cw = calcW(child);
                assign(child, lx + cw / 2, y + node.height + VG);
                lx += cw;
            });
        };
        assign(tree, 0, 0);

        // Flatten tree
        allNodes = [];
        allEdges = [];
        const collect = (node, parent = null) => {
            allNodes.push(node);
            if (parent) allEdges.push({ from: parent, to: node });
            (node.children || []).forEach(c => collect(c, node));
        };
        collect(tree);

        // Draw Edges
        const edgesG = mk('g');
        allEdges.forEach(edge => {
            const { from, to } = edge;
            const x1 = from.x, y1 = from.y + from.height;
            const x2 = to.x, y2 = to.y;
            const cy = (y1 + y2) / 2;
            const stroke = to.isContradiction ? '#ffb4ab' : edgeColor;

            const path = mk('path');
            path.setAttribute('d', `M${x1},${y1} C${x1},${cy} ${x2},${cy} ${x2},${y2}`);
            path.setAttribute('fill', 'none');
            path.setAttribute('stroke', stroke);
            path.setAttribute('stroke-width', '1.8');
            if (to.isContradiction) path.setAttribute('stroke-dasharray', '5,3');
            edgesG.appendChild(path);
            edge.pathElement = path;

            const ah = mk('polygon');
            ah.setAttribute('points', `${x2},${y2} ${x2 - 5},${y2 - 10} ${x2 + 5},${y2 - 10}`);
            ah.setAttribute('fill', stroke);
            edgesG.appendChild(ah);
            edge.arrowElement = ah;

            if (to.edgeLabel) {
                const lbl = mk('text');
                const midX = (x1 + x2) / 2;
                const offset = 12;
                let textX, anchor;
                if (x2 < x1) {
                    textX = midX - offset;
                    anchor = 'end';
                } else {
                    textX = midX + offset;
                    anchor = 'start';
                }
                lbl.setAttribute('x', textX.toString());
                lbl.setAttribute('y', (cy + 4).toString());
                lbl.setAttribute('text-anchor', anchor);
                lbl.setAttribute('fill', fontColor);
                lbl.setAttribute('font-family', 'Inter');
                lbl.setAttribute('font-size', '10');
                lbl.setAttribute('font-weight', '600');
                const lt = to.edgeLabel;
                lbl.textContent = lt;
                edgesG.appendChild(lbl);
                edge.labelElement = lbl;
            }
        });
        g.appendChild(edgesG);

        // Draw Nodes
        const nodesG = mk('g');
        allNodes.forEach((node, i) => {
            const isRoot = i === 0;
            const isConflict = node.color === '#ffb4ab' || node.color === '#ef4444';
            const bColor = (node.color && /^#[0-9a-fA-F]{6}$/.test(node.color)) ? node.color : '#e9c400';
            const r = parseInt(bColor.slice(1, 3), 16);
            const gg = parseInt(bColor.slice(3, 5), 16);
            const bb = parseInt(bColor.slice(5, 7), 16);
            const bgColor = `rgba(${r},${gg},${bb},${isLight ? 0.32 : 0.14})`;

            const ng = mk('g');
            ng.setAttribute('transform', `translate(${node.x - node.width / 2},${node.y})`);
            node.element = ng;

            if (isInteractive) {
                ng.style.opacity = '0';
                ng.style.transition = `opacity 0.5s ease ${Math.min(i * 0.07, 1.4).toFixed(2)}s`;
                ng.style.cursor = 'grab';

                ng.addEventListener('pointerdown', (e) => {
                    if (e.button !== 0) return;
                    e.stopPropagation();
                    e.preventDefault();
                    draggingNode = node;
                    nodeDragStart = { x: e.clientX, y: e.clientY };
                    ng.style.cursor = 'grabbing';
                    svg.style.cursor = 'grabbing';
                    svg.setPointerCapture(e.pointerId);
                });
            }

            if (isRoot) {
                const gr = mk('rect');
                gr.setAttribute('x', '-5'); gr.setAttribute('y', '-5');
                gr.setAttribute('width', (node.width + 10).toString()); gr.setAttribute('height', (node.height + 10).toString());
                gr.setAttribute('rx', '18');
                gr.setAttribute('fill', 'none');
                gr.setAttribute('stroke', bColor);
                gr.setAttribute('stroke-width', '10');
                gr.setAttribute('stroke-opacity', '0.18');
                gr.setAttribute('filter', 'url(#tree-glow)');
                ng.appendChild(gr);
            }

            const rect = mk('rect');
            rect.setAttribute('width', node.width.toString()); rect.setAttribute('height', node.height.toString());
            rect.setAttribute('rx', '14');
            rect.setAttribute('fill', bgColor);
            rect.setAttribute('stroke', bColor);
            rect.setAttribute('stroke-width', isRoot ? '2.5' : '1.5');
            ng.appendChild(rect);

            const icon = mk('text');
            icon.setAttribute('x', '18'); icon.setAttribute('y', (node.height / 2 + 8).toString());
            icon.setAttribute('font-family', 'Material Symbols Outlined');
            icon.setAttribute('font-size', '24');
            icon.setAttribute('fill', bColor);
            icon.textContent = isConflict ? '\ue002' : (isRoot ? '\ue838' : '\ue8d1');
            ng.appendChild(icon);

            const div = mk('line');
            div.setAttribute('x1', '47'); div.setAttribute('y1', '10');
            div.setAttribute('x2', '47'); div.setAttribute('y2', (node.height - 10).toString());
            div.setAttribute('stroke', bColor); div.setAttribute('stroke-opacity', '0.25');
            div.setAttribute('stroke-width', '1');
            ng.appendChild(div);

            node.lines.forEach((lineText, idx) => {
                const t = mk('text');
                t.setAttribute('x', '57');
                t.setAttribute('y', ((node.height / 2) - (node.lines.length * 16 / 2) + 12 + idx * 16).toString());
                t.setAttribute('fill', fontColor);
                t.setAttribute('font-family', 'Inter');
                t.setAttribute('font-size', isRoot ? '12' : '11');
                t.setAttribute('font-weight', isRoot ? '700' : '500');
                t.textContent = lineText;
                ng.appendChild(t);
            });

            const badge = mk('text');
            badge.setAttribute('x', '57'); badge.setAttribute('y', (node.height - 9).toString());
            badge.setAttribute('fill', bColor); badge.setAttribute('fill-opacity', '0.72');
            badge.setAttribute('font-family', 'Inter');
            badge.setAttribute('font-size', '9'); badge.setAttribute('font-weight', '600');
            badge.setAttribute('letter-spacing', '0.05em');
            badge.textContent = isRoot ? '◆ GỐC' : `Tầng ${node.depth}`;
            ng.appendChild(badge);

            nodesG.appendChild(ng);

            if (isInteractive) {
                setTimeout(() => { ng.style.opacity = '1'; }, 16);
            }
        });
        g.appendChild(nodesG);

        // Auto scaling/centering
        const shouldFitToView = options.fitToView === true || !isInteractive;

        if (!shouldFitToView) {
            treeTransform = { x: container.clientWidth / 2, y: 56, scale: 1 };
            applyTransform();
        } else {
            // Fit to view
            const totalWidth = (maxX - minX) + 300 + 40; 
            const totalHeight = maxBottom + 80;

            const scaleX = container.clientWidth / totalWidth;
            const scaleY = container.clientHeight / totalHeight;
            let scale = Math.min(scaleX, scaleY, 2); // Allow scaling up to 2x so single nodes don't look tiny

            // Apply a slight zoom out for padding
            scale *= 0.85;

            // Vị trí y sao cho biểu đồ nằm giữa theo chiều dọc
            const graphCenterY = maxBottom / 2;
            const yOffset = (container.clientHeight / 2) - (graphCenterY * scale);

            treeTransform = {
                x: container.clientWidth / 2,
                y: Math.max(20, yOffset), // Ensure at least 20px padding from top
                scale: scale
            };
            applyTransform();
        }
    };
})();
window.updateMindMapTheme = function (containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const isLight = !document.documentElement.classList.contains('dark');
    const fontColor = isLight ? '#162061' : '#ffffff';
    const edgeColor = isLight ? 'rgba(22,32,97,0.38)' : '#5a5230';
    const contradictionColor = '#ffb4ab';

    // Update node and edge label text colors
    const textElements = container.querySelectorAll('svg text');
    textElements.forEach(el => {
        const isIcon = el.getAttribute('font-family') === 'Material Symbols Outlined';
        const isBadge = el.textContent.includes('GỐC') || el.textContent.includes('Tầng');

        if (!isIcon && !isBadge) {
            el.setAttribute('fill', fontColor);
            el.style.fill = fontColor;
            el.setAttribute('fill-opacity', '1');
            el.style.fillOpacity = '1';
        }
    });

    // Update edge path stroke colors and arrow fill colors
    const paths = container.querySelectorAll('path');
    paths.forEach(path => {
        const isDashed = path.getAttribute('stroke-dasharray');
        if (isDashed) {
            path.setAttribute('stroke', contradictionColor);
        } else {
            path.setAttribute('stroke', edgeColor);
        }
    });

    const arrows = container.querySelectorAll('polygon');
    arrows.forEach(arrow => {
        const currentFill = arrow.getAttribute('fill');
        if (currentFill === contradictionColor) return;
        arrow.setAttribute('fill', edgeColor);
    });

    // Update node background opacity for light/dark
    const rects = container.querySelectorAll('rect');
    rects.forEach(rect => {
        const fill = rect.getAttribute('fill');
        if (fill && fill.startsWith('rgba(')) {
            const match = fill.match(/rgba\((\d+),(\d+),(\d+),([\d.]+)\)/);
            if (match) {
                const [, r, g, b] = match;
                const newOpacity = isLight ? 0.32 : 0.14;
                rect.setAttribute('fill', `rgba(${r},${g},${b},${newOpacity})`);
            }
        }
    });

    // Update initial state colors if any exist
    const initialStates = container.querySelectorAll('.initial-state');
    initialStates.forEach(state => {
        state.setAttribute('fill', fontColor);
    });

    // Force browser repaint for SVG text
    const svg = container.querySelector('svg');
    if (svg) {
        svg.style.display = 'none';
        requestAnimationFrame(() => {
            svg.style.display = 'block';
        });
    }
};

window.addEventListener('ts-theme-changed', () => {
    window.updateMindMapTheme('mindmap');
    window.updateMindMapTheme('publish-preview-network');
    
    // Cập nhật cho tất cả các biểu đồ động trong AOA Feed
    document.querySelectorAll('[id^="graph-"]').forEach(el => {
        window.updateMindMapTheme(el.id);
    });
});

window.addEventListener('ts-lang-changed', () => {
    const containers = ['mindmap', 'publish-preview-network'];
    containers.forEach(id => {
        const msgEl = document.getElementById(`${id}-empty-msg`);
        if (msgEl && window.t) {
            msgEl.textContent = window.t('coach.no_mindmap_data') || '';
        }
    });
});
