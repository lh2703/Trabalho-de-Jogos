class Collide:

    @staticmethod
    def polygon(a, b):
        """
        Mantém a mesma interface que você já usava.
        Retorna os dois shapes que colidiram.
        """

        resultado = Collide.polygon_mtv(a, b)

        if resultado is None:
            return None

        shape_a, shape_b, normal, depth = resultado

        return shape_a, shape_b

    @staticmethod
    def polygon_mtv(a, b):
        """
        Detecta colisão usando SAT e também retorna:

        shape_a
        shape_b
        normal -> direção para empurrar A para fora de B
        depth  -> profundidade da colisão
        """

        if not a.bounding_box.colliderect(b.bounding_box):
            return None

        melhor_colisao = None
        menor_overlap = float("inf")

        for shape_a in a.convex_shapes:

            for shape_b in b.convex_shapes:

                resultado = Collide.convex_mtv(
                    shape_a.points,
                    shape_b.points
                )

                if resultado is None:
                    continue

                normal, overlap = resultado

                if overlap < menor_overlap:
                    menor_overlap = overlap
                    melhor_colisao = (
                        shape_a,
                        shape_b,
                        normal,
                        overlap
                    )

        return melhor_colisao

    @staticmethod
    def convex_mtv(a, b):

        menor_overlap = float("inf")
        melhor_axis = None

        axes = Collide.axes(a) + Collide.axes(b)

        for axis in axes:

            min_a, max_a = Collide.project(a, axis)
            min_b, max_b = Collide.project(b, axis)

            # Sem colisão
            if max_a < min_b or max_b < min_a:
                return None

            overlap = min(
                max_a - min_b,
                max_b - min_a
            )

            if overlap < menor_overlap:
                menor_overlap = overlap
                melhor_axis = axis

        # -------------------------------------------------
        # Orienta a normal para sair de B em direção a A
        # -------------------------------------------------

        centro_a = (
            sum(p[0] for p in a) / len(a),
            sum(p[1] for p in a) / len(a)
        )

        centro_b = (
            sum(p[0] for p in b) / len(b),
            sum(p[1] for p in b) / len(b)
        )

        dx = centro_a[0] - centro_b[0]
        dy = centro_a[1] - centro_b[1]

        if dx * melhor_axis[0] + dy * melhor_axis[1] < 0:

            melhor_axis = (
                -melhor_axis[0],
                -melhor_axis[1]
            )

        return melhor_axis, menor_overlap

    @staticmethod
    def convex(a, b):

        return Collide.convex_mtv(a, b) is not None

    @staticmethod
    def axes(points):

        axes = []

        for i in range(len(points)):

            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]

            dx = x2 - x1
            dy = y2 - y1

            axis = (-dy, dx)

            length = (axis[0] ** 2 + axis[1] ** 2) ** 0.5

            if length > 0:

                axes.append((
                    axis[0] / length,
                    axis[1] / length
                ))

        return axes

    @staticmethod
    def project(points, axis):

        values = [
            p[0] * axis[0] + p[1] * axis[1]
            for p in points
        ]

        return min(values), max(values)