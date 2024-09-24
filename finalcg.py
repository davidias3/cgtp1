import tkinter as tk
import math

# Definindo largura e altura do canvas
WIDTH, HEIGHT = 1100, 900  # Aumentando a área de desenho

# Funções de transformação geométrica usando matrizes
def reflect_x(points):
    return [(x, -y) for x, y in points]  # Reflexão em torno do eixo X

def reflect_y(points):
    return [(-x, y) for x, y in points]  # Reflexão em torno do eixo Y

def reflect_xy(points):
    return [(-x, -y) for x, y in points]  # Reflexão em torno do eixo XY

# Funções auxiliares
def translate(points, dx, dy):
    return [(x + dx, y + dy) for x, y in points]

def rotate(points, angle, center):
    rad = math.radians(angle)
    cx, cy = center
    return [(cx + (x - cx) * math.cos(rad) - (y - cy) * math.sin(rad),
             cy + (x - cx) * math.sin(rad) + (y - cy) * math.cos(rad)) for x, y in points]

def scale(points, sx, sy, center):
    cx, cy = center
    return [(cx + (x - cx) * sx, cy + (y - cy) * sy) for x, y in points]

# Algoritmo de rasterização DDA
def dda_line(x0, y0, x1, y1):
    points = []
    dx, dy = x1 - x0, y1 - y0
    steps = max(abs(dx), abs(dy))

    # Verificação para evitar divisão por zero
    if steps == 0:
        points.append((x0, y0))
        return points

    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x0, y0
    for _ in range(int(steps) + 1):  # Corrigido para garantir que steps seja inteiro
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc
    return points

# Algoritmo de rasterização de linhas Bresenham
def bresenham_line(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return points

# Algoritmo de Bresenham para circunferência
def bresenham_circle(cx, cy, radius):
    points = []
    x, y = 0, radius
    d = 3 - 2 * radius
    while y >= x:
        points.extend([(cx + x, cy + y), (cx - x, cy + y),
                       (cx + x, cy - y), (cx - x, cy - y),
                       (cx + y, cy + x), (cx - y, cy + x),
                       (cx + y, cy - x), (cx - y, cy - x)])
        if d <= 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1
    return points

# Função para desenhar pontos no canvas
def draw_point(x, y, color="black"):
    canvas.create_oval(
        x * scale_factor + WIDTH // 2 - 2,
        -y * scale_factor + HEIGHT // 2 - 2,
        x * scale_factor + WIDTH // 2 + 2,
        -y * scale_factor + HEIGHT // 2 + 2,
        fill=color,
        outline=color
    )

# Função para calcular o centro do polígono
def calculate_center(points):
    x_coords = [x for x, y in points]
    y_coords = [y for x, y in points]
    centroid_x = sum(x_coords) / len(points)
    centroid_y = sum(y_coords) / len(points)
    return centroid_x, centroid_y

# Função para desenhar o polígono transformado
def draw_polygon(transformed_points):
    scaled_points = [(x * scale_factor + WIDTH // 2,
                      -y * scale_factor + HEIGHT // 2) for x, y in transformed_points]
    canvas.create_polygon(scaled_points, outline="black", fill="skyblue", width=2)

# Função para desenhar todas as formas armazenadas
def draw_all_shapes():
    canvas.delete("all")  # Limpa a tela antes de desenhar
    # Desenhar o eixo x e y
    canvas.create_line(WIDTH // 2, 0, WIDTH // 2, HEIGHT, fill="red")
    canvas.create_line(0, HEIGHT // 2, WIDTH, HEIGHT // 2, fill="red")

    for shape in shapes:
        for x, y in shape["points"]:
            draw_point(x, y)
        if shape["type"] == "polygon":
            draw_polygon(shape["points"])

# Função para aplicar translação
def apply_translation():
    global shapes
    try:
        dx = float(entry_dx.get())
        dy = float(entry_dy.get())
    except ValueError:
        print("Erro: Certifique-se de que dx e dy são números válidos.")
        return

    for shape in shapes:
        shape["points"] = translate(shape["points"], dx, dy)
    draw_all_shapes()

# Função para aplicar rotação
def apply_rotation():
    global shapes
    try:
        angle = float(entry_angle.get())
    except ValueError:
        print("Erro: Certifique-se de que o valor de rotação é um número válido.")
        return

    for shape in shapes:
        center = calculate_center(shape["points"])  # Usando o centro do objeto
        shape["points"] = rotate(shape["points"], angle, center)
    draw_all_shapes()

# Função para aplicar escala
def apply_scaling():
    global shapes
    try:
        sx = float(entry_sx.get())
        sy = float(entry_sy.get())
    except ValueError:
        print("Erro: Certifique-se de que sx e sy são números válidos.")
        return

    for shape in shapes:
        center = calculate_center(shape["points"])  # Usando o centro do objeto
        shape["points"] = scale(shape["points"], sx, sy, center)
    draw_all_shapes()

# Função para aplicar reflexão com eixo dinâmico
def apply_reflection(axis):
    global shapes
    for shape in shapes:
        if axis == 'X':
            shape["points"] = reflect_x(shape["points"])
        elif axis == 'Y':
            shape["points"] = reflect_y(shape["points"])
        elif axis == 'XY':
            shape["points"] = reflect_xy(shape["points"])
    draw_all_shapes()

# Função de recorte Cohen-Sutherland
def apply_cohen_sutherland():
    global shapes
    for shape in shapes:
        if shape["type"] == "line" and len(shape["points"]) > 1:
            clipped_points = cohen_sutherland(shape["points"])
            if clipped_points:
                shape["points"] = clipped_points
    draw_all_shapes()

# Função de recorte Liang-Barsky
def apply_liang_barsky():
    global shapes
    for shape in shapes:
        if shape["type"] == "line" and len(shape["points"]) > 1:
            clipped_points = liang_barsky(shape["points"])
            if clipped_points:
                shape["points"] = clipped_points
    draw_all_shapes()

# Função para recortar uma linha usando Cohen-Sutherland
def cohen_sutherland(points):
    x_min, y_min = -5, -5
    x_max, y_max = 5, 5
    def compute_code(x, y):
        code = 0
        if x < x_min: code |= 1
        elif x > x_max: code |= 2
        if y < y_min: code |= 4
        elif y > y_max: code |= 8
        return code

    x0, y0 = points[0]
    x1, y1 = points[-1]
    code0 = compute_code(x0, y0)
    code1 = compute_code(x1, y1)
    while True:
        if code0 == 0 and code1 == 0:
            return [(x0, y0), (x1, y1)]
        elif code0 & code1:
            return []
        else:
            x, y = 0, 0
            code_out = code0 if code0 else code1
            if code_out & 8:
                x = x0 + (x1 - x0) * (y_max - y0) / (y1 - y0)
                y = y_max
            elif code_out & 4:
                x = x0 + (x1 - x0) * (y_min - y0) / (y1 - y0)
                y = y_min
            elif code_out & 2:
                y = y0 + (y1 - y0) * (x_max - x0) / (x1 - x0)
                x = x_max
            elif code_out & 1:
                y = y0 + (y1 - y0) * (x_min - x0) / (x1 - x0)
                x = x_min

            if code_out == code0:
                x0, y0 = x, y
                code0 = compute_code(x0, y0)
            else:
                x1, y1 = x, y
                code1 = compute_code(x1, y1)

# Função para recortar uma linha usando Liang-Barsky
def liang_barsky(points):
    x_min, y_min = -5, -5
    x_max, y_max = 5, 5
    x0, y0 = points[0]
    x1, y1 = points[-1]
    dx = x1 - x0
    dy = y1 - y0
    p = [-dx, dx, -dy, dy]
    q = [x0 - x_min, x_max - x0, y0 - y_min, y_max - y0]
    u1, u2 = 0.0, 1.0

    for i in range(4):
        if p[i] == 0:
            if q[i] < 0:
                return []
        else:
            t = q[i] / p[i]
            if p[i] < 0:
                if u1 < t:
                    u1 = t
            else:
                if u2 > t:
                    u2 = t

    if u1 > u2:
        return []

    x_start = x0 + u1 * dx
    y_start = y0 + u1 * dy
    x_end = x0 + u2 * dx
    y_end = y0 + u2 * dy
    return [(x_start, y_start), (x_end, y_end)]

# Função para limpar a tela e redefinir as alterações
def clear_canvas():
    global shapes, points
    shapes = [{"type": "polygon", "points": original_points[:]}]  # Restaura o quadrado original
    draw_all_shapes()  # Redesenha o polígono original

# Eventos de mouse para desenho
def draw_line_or_circle(event):
    global start_x, start_y, draw_mode, drawing, line_points, shapes

    if not drawing:  # Primeiro clique, definindo o ponto inicial ou o centro
        start_x = (event.x - WIDTH // 2) / scale_factor
        start_y = (HEIGHT // 2 - event.y) / scale_factor
        drawing = True
    else:  # Segundo clique, definindo o ponto final ou o raio
        end_x = (event.x - WIDTH // 2) / scale_factor
        end_y = (HEIGHT // 2 - event.y) / scale_factor
        drawing = False

        if draw_mode == 'dda_line':
            line_points = dda_line(int(start_x), int(start_y), int(end_x), int(end_y))
            shapes.append({"type": "line", "points": line_points})
        elif draw_mode == 'bresenham_line':
            line_points = bresenham_line(int(start_x), int(start_y), int(end_x), int(end_y))
            shapes.append({"type": "line", "points": line_points})
        elif draw_mode == 'bresenham_circle':
            # O raio é calculado como a distância entre o centro e o ponto clicado
            radius = int(math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2))
            circle_points = bresenham_circle(int(start_x), int(start_y), radius)
            shapes.append({"type": "circle", "points": circle_points})

        # Desenhar todos os pontos de todas as formas
        draw_all_shapes()

def set_draw_mode(mode):
    global draw_mode
    draw_mode = mode

# Interface gráfica com tkinter
root = tk.Tk()
root.title("Transformações Geométricas 2D")

# Canvas para desenhar o polígono
scale_factor = 20
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

# Frame para os controles de transformação e desenho
frame_controls = tk.Frame(root)
frame_controls.pack(side=tk.BOTTOM, pady=10)

# Parâmetros de entrada para transformações
tk.Label(frame_controls, text="Translação (dx, dy):").grid(row=0, column=0, sticky='e')
entry_dx = tk.Entry(frame_controls, width=5)
entry_dx.grid(row=0, column=1)
entry_dx.insert(0, "0")
entry_dy = tk.Entry(frame_controls, width=5)
entry_dy.grid(row=0, column=2)
entry_dy.insert(0, "0")

tk.Label(frame_controls, text="Rotação (graus):").grid(row=0, column=3, sticky='e')
entry_angle = tk.Entry(frame_controls, width=5)
entry_angle.grid(row=0, column=4)
entry_angle.insert(0, "0")

tk.Label(frame_controls, text="Escala (sx, sy):").grid(row=0, column=5, sticky='e')
entry_sx = tk.Entry(frame_controls, width=5)
entry_sx.grid(row=0, column=6)
entry_sx.insert(0, "1")
entry_sy = tk.Entry(frame_controls, width=5)
entry_sy.grid(row=0, column=7)
entry_sy.insert(0, "1")

# Botões para aplicar transformações separadamente
btn_translate = tk.Button(frame_controls, text="Aplicar Translação", command=apply_translation)
btn_translate.grid(row=1, column=0, columnspan=2, pady=5)

btn_rotate = tk.Button(frame_controls, text="Aplicar Rotação", command=apply_rotation)
btn_rotate.grid(row=1, column=2, columnspan=2, pady=5)

btn_scale = tk.Button(frame_controls, text="Aplicar Escala", command=apply_scaling)
btn_scale.grid(row=1, column=4, columnspan=2, pady=5)

# Botões para aplicar reflexão diretamente com eixo específico
reflect_x_button = tk.Button(frame_controls, text="Refletir X", command=lambda: apply_reflection('X'))
reflect_x_button.grid(row=1, column=6, pady=5)

reflect_y_button = tk.Button(frame_controls, text="Refletir Y", command=lambda: apply_reflection('Y'))
reflect_y_button.grid(row=1, column=7, pady=5)

reflect_xy_button = tk.Button(frame_controls, text="Refletir XY", command=lambda: apply_reflection('XY'))
reflect_xy_button.grid(row=1, column=8, pady=5)

# Botões para definir o modo de desenho com o mouse
btn_dda_mode = tk.Button(frame_controls, text="Modo Linha DDA", command=lambda: set_draw_mode('dda_line'))
btn_dda_mode.grid(row=2, column=0, columnspan=2, pady=5)

btn_bresenham_line_mode = tk.Button(frame_controls, text="Modo Linha Bresenham", command=lambda: set_draw_mode('bresenham_line'))
btn_bresenham_line_mode.grid(row=2, column=2, columnspan=2, pady=5)

btn_bresenham_circle_mode = tk.Button(frame_controls, text="Modo Circunferência", command=lambda: set_draw_mode('bresenham_circle'))
btn_bresenham_circle_mode.grid(row=2, column=4, columnspan=2, pady=5)

# Botão para aplicar o recorte Cohen-Sutherland
btn_cohen_sutherland = tk.Button(frame_controls, text="Recorte Cohen-Sutherland", command=apply_cohen_sutherland)
btn_cohen_sutherland.grid(row=2, column=6, pady=5)

# Botão para aplicar o recorte Liang-Barsky
btn_liang_barsky = tk.Button(frame_controls, text="Recorte Liang-Barsky", command=apply_liang_barsky)
btn_liang_barsky.grid(row=2, column=7, pady=5)

# Botão para limpar a tela
btn_clear = tk.Button(frame_controls, text="Limpar Tela", command=clear_canvas)
btn_clear.grid(row=2, column=8, pady=5)

# Eventos de mouse para desenho
canvas.bind("<Button-1>", draw_line_or_circle)

# Pontos iniciais do polígono (quadrado)
original_points = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
points = original_points[:]
shapes = [{"type": "polygon", "points": points}]  # Armazenando as formas desenhadas

# Desenhar o polígono inicial
draw_all_shapes()

# Variáveis para armazenar o modo de desenho e estado de desenho
draw_mode = None
drawing = False

# Iniciar a interface
root.mainloop()
