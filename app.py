from flask import Flask, render_template, request, redirect, url_for
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpBinary, LpInteger
from items import load_items, save_items
import locale

app = Flask(__name__)
locale.setlocale(locale.LC_ALL, '')

def format_number(n):
    return "{:,.2f}".format(n).replace(",", " ").replace(".00", ".00")

# Главная страница: подбор товаров
@app.route("/", methods=["GET", "POST"])
def calculate():
    results = []
    total = 0
    target = ""
    max_per_type = ""

    if request.method == "POST":
        target = float(request.form["target"])
        max_per_type = int(request.form["max_per_type"])
        items = load_items()

        prob = LpProblem("Item_Selection", LpMaximize)
        x = [LpVariable(f"x{i}", lowBound=0, upBound=min(item["qty"], max_per_type), cat=LpInteger)
             for i, item in enumerate(items)]
        f = [LpVariable(f"f{i}", cat=LpBinary) for i in range(len(items))]

        prob += lpSum([x[i] * items[i]["price"] for i in range(len(items))])
        prob += lpSum([x[i] * items[i]["price"] for i in range(len(items))]) <= target

        for i in range(len(items)):
            prob += x[i] <= f[i] * max_per_type

        prob.solve()

        for i in range(len(items)):
            count = int(x[i].varValue)
            if count > 0:
                subtotal = count * items[i]["price"]
                results.append({
                    "index": i,
                    "name": items[i]["name"],
                    "count": count,
                    "subtotal": format_number(subtotal)
                })
                total += subtotal

        return render_template("result.html",
                               results=results,
                               total=format_number(total),
                               target=format_number(target),
                               request=request)

    return render_template("result.html", results=[], total=0, target=target, request=request)

# Подтверждение выполненного подбора — обновление количества
@app.route("/done", methods=["POST"])
def done():
    used_items = request.json["used"]
    items = load_items()
    for entry in used_items:
        i = entry["index"]
        count = entry["count"]
        items[i]["qty"] = max(0, items[i]["qty"] - count)
    save_items(items)
    return {"status": "updated"}

# Страница управления товарами
@app.route("/manage")
def manage_items():
    items = load_items()
    return render_template("manage.html", items=items)

# Добавление нового товара
@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        new_item = {
            "name": request.form["name"],
            "price": float(request.form["price"]),
            "qty": int(request.form["qty"])
        }
        items = load_items()
        items.append(new_item)
        save_items(items)
        return redirect(url_for("manage_items"))
    return render_template("add_item.html")

# Редактирование товара
@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_item(index):
    items = load_items()
    if request.method == "POST":
        items[index]["name"] = request.form["name"]
        items[index]["price"] = float(request.form["price"])
        items[index]["qty"] = int(request.form["qty"])
        save_items(items)
        return redirect(url_for("manage_items"))
    return render_template("edit_item.html", item=items[index], index=index)

# Удаление товара
@app.route("/delete/<int:index>", methods=["POST"])
def delete_item(index):
    items = load_items()
    if 0 <= index < len(items):
        del items[index]
        save_items(items)
    return redirect(url_for("manage_items"))

if __name__ == "__main__":
    app.run(debug=True)
