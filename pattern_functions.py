from models import db, ModelPattern, ModelClothing, Pattern


def add_pattern(app, name, sizes, photo):
    with app.app_context():
        pattern = Pattern(name=name, sizes=sizes, photo=photo)
        db.session.add(pattern)
        db.session.commit()

        print(f"Выкройка добавлена: ID - {pattern.id}, Название - {name}, Размер - {sizes}, Фото - {photo}")


def update_pattern(app, pattern_id, new_name, new_sizes, new_photo):
    with app.app_context():
        pattern = Pattern.query.get(pattern_id)

        if pattern:
            pattern.name = new_name
            pattern.sizes = new_sizes
            pattern.photo = new_photo
            db.session.commit()

            print(
                f"Выкройка обновлена: ID - {pattern_id}, Название - {new_name}, Размер - {new_sizes}, Фото - {new_photo}")
        else:
            print(f"Выкройка с ID {pattern_id} не найдена.")


def delete_pattern(app, pattern_id):
    with app.app_context():
        pattern = Pattern.query.get(pattern_id)
        if pattern:
            # ModelPattern
            model_patterns = ModelPattern.query.filter_by(pattern_id=pattern_id).all()
            for model_pattern in model_patterns:
                db.session.delete(model_pattern)

            # Pattern
            db.session.delete(pattern)
            db.session.commit()

            print(f"Выкройка удалена: ID - {pattern_id}, Название - {pattern.name}")
        else:
            print(f"Выкройка с ID {pattern_id} не найдена.")


def create_model_pattern(app, model_clothing_id, pattern_id):
    with app.app_context():
        model_clothing = ModelClothing.query.get(model_clothing_id)
        pattern = Pattern.query.get(pattern_id)

        if model_clothing and pattern and model_clothing.name == pattern.name:
            existing_pattern = ModelPattern.query.filter_by(
                model_clothing_id=model_clothing.id,
                pattern_id=pattern.id
            ).first()

            if existing_pattern:
                return "Связь уже существует"

            model_pattern = ModelPattern(model_clothing_id=model_clothing.id, pattern_id=pattern.id)
            db.session.add(model_pattern)
            db.session.commit()

            return None
        else:
            return "Ошибка: Модель не найдена или имена не совпадают"


