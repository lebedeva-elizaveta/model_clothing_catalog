import secrets

from flask import Flask, request, redirect, url_for, render_template, flash
from markupsafe import escape
import random
from flask_migrate import Migrate
from sqlalchemy.orm import joinedload

import models_functions
import pattern_functions
from models import db, ModelClothing, ModelPhoto, Pattern, ModelPattern, AdditionalInfoForModelClothing
from models_functions import add_model_clothing, update_model_clothing, delete_model_clothing
from pattern_functions import add_pattern, update_pattern, delete_pattern, create_model_pattern
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/Database_clothes'
db.init_app(app)
migrate = Migrate(app, db)


def clear_tables():
    with app.app_context():
        try:
            sql_query = "TRUNCATE TABLE model_clothing RESTART IDENTITY CASCADE"
            db.session.execute(db.text(sql_query))
            sql_query = "TRUNCATE TABLE pattern RESTART IDENTITY CASCADE"
            db.session.execute(db.text(sql_query))
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")


def add_sample_data():
    # ModelClothing
    names = ["платье", "юбка", "футболка", "рубашка", "брюки", "джинсы", "толстовка", "лонгслив", "шорты", "блузка",
             "кофта", "штаны"]
    descriptions = ["text1", "text2", "text3"]

    for _ in range(1000):
        name = random.choice(names)
        description = random.choice(descriptions)
        material_consumption = round(random.uniform(5, 10), 2)

        clothing = ModelClothing(name=name, material_consumption=material_consumption)
        db.session.add(clothing)
        db.session.flush()

        photo_name = f"{name}_{clothing.id}.jpg"
        photo = ModelPhoto(name=photo_name, model_clothing_id=clothing.id)
        db.session.add(photo)

        clothing.photos = [photo]
        clothing.description = description

        db.session.commit()

        # ModelPhoto
    for _ in range(1000):
        name = random.choice(names)
        descriptions = random.choice(descriptions)
        material_consumption = round(random.uniform(5, 10), 2)

        clothing = ModelClothing(name=name, material_consumption=material_consumption)
        db.session.add(clothing)
        db.session.flush()

        photo_name = f"{name}_{clothing.id}.jpg"
        photo = ModelPhoto(name=photo_name, model_clothing_id=clothing.id)
        db.session.add(photo)

        clothing.photos = [photo]
        clothing.description = descriptions

        db.session.commit()

    # Pattern
    pattern_sizes = ["XS", "S", "M", "L", "XL"]

    for _ in range(1000):
        name = random.choice(names)
        size = random.choice(pattern_sizes)
        pattern = Pattern(name=name, sizes=size)
        db.session.add(pattern)
        db.session.commit()
        photo = f"{name}_{pattern.id}.jpg"
        pattern.photo = photo

    db.session.commit()

    # ModelPattern
    model_clothings = ModelClothing.query.all()
    patterns = Pattern.query.all()

    for model in model_clothings:
        pattern_name = model.name
        pattern = next((p for p in patterns if p.name == pattern_name), None)
        if pattern:
            model_pattern = ModelPattern(model_clothing_id=model.id, pattern_id=pattern.id)
            db.session.add(model_pattern)

    db.session.commit()

    # AdditionalInfoForModelClothing
    care_instructions_list = ["инструкция 1", "инструкция 2", "инструкция 3"]
    materials_list = ["хлопок", "полиэстер", "шелк", "полиэфир"]

    for i, model in enumerate(model_clothings):
        care_instructions = random.choice(care_instructions_list)
        materials = random.choice(materials_list)
        cost = round(random.uniform(5000, 10000), 2)

        additional_info = AdditionalInfoForModelClothing(
            model_clothing_id=model.id,
            care_instructions=care_instructions,
            materials=materials,
            cost=cost,
        )

        db.session.add(additional_info)
        db.session.commit()
    pass


def display_first_10_records():
    first_10_clothing = ModelClothing.query.limit(10).all()
    print("Первые 10 записей в ModelClothing:")
    for record in first_10_clothing:
        print(
            f"ID: {escape(record.id)}, Название: {escape(record.name)}, Расход материала: {escape(record.material_consumption)}, "
            f"Description: {escape(record.description)}")

        for photo in record.photos:
            print(f"  Фото ID: {escape(photo.id)}, Название фото: {escape(photo.name)}")

    first_10_patterns = Pattern.query.limit(10).all()
    print("\nПервые 10 записей в Pattern:")
    for record in first_10_patterns:
        print(
            f"ID: {escape(record.id)}, Название: {escape(record.name)}, Размер: {escape(record.sizes)}, "
            f"Название фото: {escape(record.photo)}")

    first_10_model_patterns = ModelPattern.query.limit(10).all()
    print("\nПервые 10 записей в ModelPattern:")
    for record in first_10_model_patterns:
        print(f"Model Clothing ID: {escape(record.model_clothing_id)}, Pattern ID: {escape(record.pattern_id)}")

    first_10_additional_info = AdditionalInfoForModelClothing.query.limit(10).all()
    print("\nПервые 10 записей в AdditionalInfoForModelClothing:")
    for record in first_10_additional_info:
        print(
            f"Model Clothing ID: {escape(record.model_clothing_id)}, Инструкции по уходу: {escape(record.care_instructions)}, "
            f"Материал: {escape(record.materials)}, Цена: {escape(record.cost)}")

    return "Проверьте в своей консоли 10 первых записей."


@app.route('/')
def home():
    models = (ModelClothing.query.join(AdditionalInfoForModelClothing).all())
    patterns = Pattern.query.all()

    models_count = len(models)
    patterns_count = len(patterns)

    # средняя стоимость моделей
    total_cost = sum(model.additional_info.cost for model in models if model.additional_info
                     and model.additional_info.cost is not None)
    average_cost = total_cost / models_count if models_count > 0 else 0

    # статистика кол-во моделей каждого типа
    categories_count = {}
    for model in models:
        name = model.name
        if name in categories_count:
            categories_count[name] += 1
        else:
            categories_count[name] = 1

    return render_template('home.html', models_count=models_count, patterns_count=patterns_count,
                           average_cost=average_cost, categories_count=categories_count)


@app.route('/model_clothing')
def model_clothing():
    page = request.args.get('page', 1, type=int)
    per_page = 15

    name_filter = request.args.get('name', '')
    material_filter = request.args.get('material', '')
    min_cost_filter = request.args.get('min_cost', '')
    max_cost_filter = request.args.get('max_cost', '')

    filters = []

    if name_filter:
        filters.append(ModelClothing.name.ilike(f"%{name_filter}%"))
    if material_filter:
        filters.append(AdditionalInfoForModelClothing.materials.ilike(f"%{material_filter}%"))
    if min_cost_filter and max_cost_filter:
        filters.append(AdditionalInfoForModelClothing.cost.between(float(min_cost_filter), float(max_cost_filter)))

    if filters:
        models = (
            ModelClothing.query
            .join(AdditionalInfoForModelClothing)
            .filter(and_(*filters))
            .options(joinedload(ModelClothing.additional_info))
            .paginate(page=page, per_page=per_page)
        )
    else:
        models = ModelClothing.query.order_by(ModelClothing.id.asc()).paginate(page=page, per_page=per_page)

    name_options = ['платье', 'юбка', 'футболка', 'рубашка', 'брюки', 'джинсы', 'толстовка', 'лонгслив', 'шорты',
                    'блузка', 'кофта', 'штаны']
    materials_options = ["хлопок", "полиэстер", "шелк", "полиэфир"]

    return render_template('model_clothing.html', models=models, name_options=name_options,
                           materials_options=materials_options)


@app.route('/pattern')
def pattern():
    page = request.args.get('page', 1, type=int)
    per_page = 15

    size = request.args.get('size', '')
    name = request.args.get('name', '')

    filter_conditions = []

    if size:
        filter_conditions.append(Pattern.sizes == size)

    if name:
        filter_conditions.append(Pattern.name == name)

    filter_condition = and_(*filter_conditions)

    if filter_conditions:
        patterns = Pattern.query.filter(filter_condition).paginate(page=page, per_page=per_page)
    else:
        patterns = Pattern.query.paginate(page=page, per_page=per_page)

    name_options = ['платье', 'юбка', 'футболка', 'рубашка', 'брюки', 'джинсы', 'толстовка', 'лонгслив', 'шорты',
                    'блузка', 'кофта', 'штаны']

    return render_template('pattern.html', patterns=patterns, options=['XS', 'S', 'M', 'L', 'XL'],
                           name_options=name_options)


@app.route('/model_pattern')
def model_pattern():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    patterns = ModelPattern.query.paginate(page=page, per_page=per_page)

    return render_template('model_pattern.html', patterns=patterns)


@app.route('/model_clothing/add', methods=['GET', 'POST'])
def add_model_clothing():
    if request.method == 'POST':
        name = request.form.get('name')
        material_consumption = request.form.get('material_consumption')
        description = request.form.get('description')
        photo_name = request.form.get('photo_name')
        care_instructions = request.form.get('care_instructions')
        materials = request.form.get('materials')
        cost = request.form.get('cost')

        # является ли material_consumption и cost числовыми значениями
        if not material_consumption.isnumeric():
            flash('Расход материала должен быть числовым значением.', 'danger')
            return render_template('add_model_clothing.html')

        if not cost.isnumeric():
            flash('Цена должна быть числовым значением.', 'danger')
            return render_template('add_model_clothing.html')

        models_functions.add_model_clothing(
            app,
            name,
            material_consumption,
            description,
            photo_name,
            care_instructions,
            materials,
            cost
        )

        flash('Модель успешно добавлена.', 'success')
        return redirect(url_for('model_clothing'))

    return render_template('add_model_clothing.html')


@app.route('/update_model_clothing/<int:model_id>', methods=['GET', 'POST'])
def update_model_clothing(model_id):
    clothing = ModelClothing.query.get(model_id)

    if request.method == 'POST':
        new_name = request.form.get('new_name')
        new_material_consumption = request.form.get('new_material_consumption')
        new_description = request.form.get('new_description')
        new_photo_name = request.form.get('new_photo_name')
        care_instructions = request.form.get('care_instructions')
        materials = request.form.get('materials')
        cost = request.form.get('cost')

        try:
            new_material_consumption = float(new_material_consumption)
        except ValueError:
            flash('Новый расход материала должен быть числовым значением.', 'danger')
            return render_template('update_model_clothing.html', clothing=clothing)

        try:
            cost = float(cost)
        except ValueError:
            flash('Цена должна быть числовым значением.', 'danger')
            return render_template('update_model_clothing.html', clothing=clothing)

        models_functions.update_model_clothing(app, model_id, new_name, new_material_consumption, new_description,
                                               new_photo_name, care_instructions, materials, cost)

        flash('Модель успешно обновлена.', 'success')
        return redirect(url_for('model_clothing'))

    return render_template('update_model_clothing.html', clothing=clothing)


@app.route('/delete_model_clothing/<int:model_id>', methods=['GET', 'POST'])
def delete_model_clothing_route(model_id):
    if request.method == 'POST':
        models_functions.delete_model_clothing(app, model_id)
        flash('Модель успешно удалена.', 'success')
        return redirect(url_for('model_clothing'))

    model_clothing = ModelClothing.query.get(model_id)
    if model_clothing:
        return render_template('delete_model_clothing.html', model_clothing=model_clothing)
    else:
        return flash('Модель не найдена.', 'danger')


@app.route('/pattern/add', methods=['GET', 'POST'])
def add_pattern():
    if request.method == 'POST':
        name = request.form.get('name')
        sizes = request.form.get('sizes')
        photo = request.form.get('photo')

        pattern_functions.add_pattern(app, name, sizes, photo)
        flash('Выкройка успешно добавлена.', 'success')
        return redirect(url_for('pattern'))

    return render_template('add_pattern.html')


@app.route('/pattern/update/<int:pattern_id>', methods=['GET', 'POST'])
def update_pattern(pattern_id):
    if request.method == 'POST':
        new_name = request.form.get('new_name')
        new_sizes = request.form.get('new_sizes')
        new_photo = request.form.get('new_photo')

        pattern_functions.update_pattern(app, pattern_id, new_name, new_sizes, new_photo)

        return redirect(url_for('pattern'))

    return render_template('update_pattern.html', pattern_id=pattern_id)


@app.route('/pattern/delete/<int:pattern_id>', methods=['GET', 'POST'])
def delete_pattern(pattern_id):
    if request.method == 'POST':
        pattern_functions.delete_pattern(app, pattern_id)
        flash('Выкройка успешно удалена.', 'success')
        return redirect(url_for('pattern'))

    pattern = Pattern.query.get(pattern_id)
    if pattern:
        return render_template('delete_pattern.html', pattern=pattern)
    else:
        return flash('Выкройка не найдена.', 'danger')


@app.route('/create_model_pattern', methods=['GET', 'POST'])
def create_model_pattern_route():
    if request.method == 'POST':
        model_clothing_id = request.form.get('model_clothing_id')
        pattern_id = request.form.get('pattern_id')

        result_message = create_model_pattern(app, model_clothing_id, pattern_id)

        if not result_message:
            flash('Связь успешно добавлена.', 'success')
        else:
            return render_template('create_model_pattern_error.html', error_message=result_message)

    return render_template('model_pattern_table.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # clear_tables()
        # add_sample_data()


    # display_first_10_records()
    def main():
        while True:
            print("\nChoose an action:")
            print("1. Добавить модель одежды")
            print("2. Обновить модель одежды")
            print("3. Удалить модель одежды")
            print("4. Добавить выкройку")
            print("5. Обновить выкройку")
            print("6. Удалить выкройку")
            print("7. Связать выкройку и модель")
            print("0. Выход")

            choice = input("Выберите действие: ")

            if choice == "0":
                break
            elif choice == "1":
                try:
                    name = input("Название: ").strip()
                    if not name:
                        print("Название не может быть пустым.")
                        continue
                    material_consumption = float(input("Расходы материала: "))
                    description = input("Описание: ")
                    photo_name = input("Название фото (нажмите Enter, чтобы сгенерировать): ")
                    add_model_clothing(app, name, material_consumption, description, photo_name)
                except ValueError:
                    print("Некорректные данные. Попробуйте еще раз.")
            elif choice == "2":
                try:
                    model_id = int(input("ID модели: "))
                    new_name = input("Новое название: ")
                    new_material_consumption = float(input("Расход материала: "))
                    new_description = input("Описание: ")
                    new_photo_name = input("Название фото (нажмите Enter, чтобы не менять): ")
                    update_model_clothing(app, model_id, new_name, new_material_consumption, new_description,
                                          new_photo_name)
                except ValueError:
                    print("Некорректные данные. Попробуйте еще раз.")
            elif choice == "3":
                try:
                    model_id = int(input("ID модели: "))
                    delete_model_clothing(app, model_id)
                except ValueError:
                    print("Некорректные данные. Попробуйте еще раз.")
            elif choice == "4":
                try:
                    name = input("Название: ")
                    sizes = input("Размер: ")
                    photo = input("Название фото: ")
                    add_pattern(app, name, sizes, photo)
                except ValueError:
                    print("Некорректные данные. Попробуйте еще раз.")
            elif choice == "5":
                try:
                    pattern_id = int(input("ID выкройки: "))
                    new_name = input("Новое название: ")
                    new_sizes = input("Размер: ")
                    new_photo_name = input("Фото: ")
                    update_pattern(app, pattern_id, new_name, new_sizes, new_photo_name)
                except ValueError:
                    print("Некорректные данные. Попробуйте еще раз.")
            elif choice == "6":
                try:
                    pattern_id = int(input("ID выкройки: "))
                    delete_pattern(app, pattern_id)
                except ValueError:
                    print("Некорректные данные. Попробуйте еще раз.")
            elif choice == "7":
                try:
                    model_id = int(input("ID модели:"))
                    pattern_id = int(input("ID выкройки:"))
                    create_model_pattern(app, model_id, pattern_id)
                except ValueError:
                    print("Некорректные данные. Попробуйте еще раз.")
            else:
                print("Некорректные данные. Попробуйте еще раз.")

    app.run(debug=True)
