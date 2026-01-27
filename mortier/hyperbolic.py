import numpy as np

def build_adjacency(faces, tol=1e-6):
    """
    Construit un dictionnaire d'adjacence pour un pavage euclidien.
    Chaque face est une liste d'objets avec .x et .y.
    Deux faces sont considérées adjacentes si elles partagent deux sommets (même arête).
    """
    # On va identifier chaque arête par ses deux extrémités arrondies
    edge_map = {}
    adjacency = {}

    def rounded(p):
        return (round(p.x, 6), round(p.y, 6))

    for i, face in enumerate(faces):
        n = len(face.vertices)
        for k in range(n):
            a = rounded(face.vertices[k])
            b = rounded(face.vertices[(k + 1) % n])
            # Pour l’arête, on stocke les extrémités triées (indépendant du sens)
            key = tuple(sorted([a, b]))
            if key not in edge_map:
                edge_map[key] = (i, k)
            else:
                # arête déjà vue → les deux faces sont voisines
                i0, e0 = edge_map[key]
                i1, e1 = i, k
                adjacency[(i0, e0)] = i1
                adjacency[(i1, e1)] = i0
    return adjacency
def mobius_transform(z, a, b, c, d):
    return (a*z + b)/(c*z + d)

def mobius_map_segment(C, D, A, B):
    """
    Calcule une transformation de Möbius f(z) = e^{iθ} * (z - a)/(1 - conj(a)*z)
    qui envoie le segment C->D sur A->B.

    C, D : points de l'arête à transformer (complex)
    A, B : points cibles (complex)

    Retour : fonction f(z) appliquée à tout z
    """
    # Translation et rotation simple via Möbius : z -> (z-C)/(z-D) puis ajustement
    # Normalisation : on envoie C->0, D->1
    z = lambda w: (w - C)/(D - C)
    target = lambda w: (w - A)/(B - A)

    def f(w):
        return target(z(w))

    return f

def choose_central_face(faces):
    # Calculer barycentre de toutes les faces
    all_pts = np.array([[v.x, v.y] for f in faces for v in f.vertices])
    barycenter = np.mean(all_pts, axis=0)

    # Choisir la face dont le centre est le plus proche
    min_dist = float('inf')
    center_idx = 0
    for i, f in enumerate(faces):
        f_center = np.mean([[v.x, v.y] for v in f.vertices], axis=0)
        dist = np.linalg.norm(f_center - barycenter)
        if dist < min_dist:
            min_dist = dist
            center_idx = i
    return center_idx

def propagate_hyperbolic_paving(faces):
    # Construction d'adjacence simple : faces partageant un bord
    edge_map = {}
    adjacency = {}
    def rounded(p):
        return (round(p.x,6), round(p.y,6))
    for i,f in enumerate(faces):
        n = len(f.vertices)
        for k in range(n):
            a = rounded(f.vertices[k])
            b = rounded(f.vertices[(k+1)%n])
            key = tuple(sorted([a,b]))
            if key not in edge_map:
                edge_map[key] = (i,k)
            else:
                i0,e0 = edge_map[key]
                i1,e1 = i,k
                adjacency[(i0,e0)] = i1
                adjacency[(i1,e1)] = i0

    # Placer la face centrale
    start = choose_central_face(faces)
    placed = {}
    queue = []

    f0 = faces[start]
    placed[start] = np.array([complex(v.x,v.y) for v in f0.vertices])
    placed[start] -= np.mean(placed[start])
    queue.append(start)

    while queue:
        i = queue.pop(0)
        f = placed[i]
        for e_idx in range(len(f)):
            key = (i,e_idx)
            if key not in adjacency:
                continue
            j = adjacency[key]
            if j in placed:
                continue

            # Arête partagée
            A = f[e_idx]
            B = f[(e_idx+1)%len(f)]
            f_j = np.array([complex(v.x,v.y) for v in faces[j].vertices])

            # Trouver l'arête correspondante dans f_j
            shared_idx = None
            for k in range(len(f_j)):
                C = f_j[k]
                D = f_j[(k+1)%len(f_j)]
                if np.isclose(C,A) and np.isclose(D,B) or np.isclose(C,B) and np.isclose(D,A):
                    shared_idx = k
                    break

            if shared_idx is None:
                shift = (A+B)/2 - np.mean(f_j)
                placed[j] = f_j + shift
            else:
                # Approximation : translation + rotation pour aligner arête
                C = f_j[shared_idx]
                D = f_j[(shared_idx+1)%len(f_j)]
                f_map = lambda z: ((B-A)/(D-C))*(z-C)+A
                placed[j] = np.array([f_map(v) for v in f_j])

            queue.append(j)

    # Normaliser dans le disque unité
    all_pts = np.concatenate(list(placed.values()))
    max_norm = np.max(np.abs(all_pts))
    for k in placed:
        placed[k] /= max_norm

    return placed
