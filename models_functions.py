from models import db, ModelClothing, ModelPhoto, AdditionalInfoForModelClothing, ModelPattern


def add_model_clothing(app, name, material_consumption, description, photo_name=None,
                       care_instructions=None, materials=None, cost=None):
    with app.app_context():
        # ModelClothing
        clothing = ModelClothing(name=name, material_consumption=material_consumption, description=description)
        db.session.add(clothing)
        db.session.flush()  # фиксирует изменения и делает доступным id

        # ModelPhoto
        if not photo_name:
            photo_name = f"{name}_{clothing.id}.jpg"
        photo = ModelPhoto(name=photo_name, model_clothing_id=clothing.id)
        db.session.add(photo)
        clothing.photos = [photo]

        # AdditionalInfoForModelClothing
        additional_info = AdditionalInfoForModelClothing(
            model_clothing_id=clothing.id,
            care_instructions=care_instructions,
            materials=materials,
            cost=cost,
        )
        db.session.add(additional_info)

        db.session.commit()

        print(f"Модель одежды добавлена: ID - {clothing.id}, Название - {name}, Расход материала - {material_consumption}, "
              f"Описание - {description}, Название фото - {photo_name}")
        print(f"Доп. информация добавлена: Инструкция по уходу - {care_instructions}, Материал - {materials}, Цена - {cost}")


def update_model_clothing(app, model_id, new_name, new_material_consumption, new_description, new_photo_name=None,
                           care_instructions=None, materials=None, cost=None):
    with app.app_context():
        clothing = ModelClothing.query.get(model_id)
        if clothing:
            clothing.name = new_name
            clothing.material_consumption = new_material_consumption
            clothing.description = new_description

            # ModelPhoto
            if new_photo_name is not None:
                photo = ModelPhoto.query.filter_by(model_clothing_id=model_id).first()
                if photo:
                    photo.name = new_photo_name

            # AdditionalInfoForModelClothing
            additional_info = AdditionalInfoForModelClothing.query.get(model_id)
            if additional_info:
                if care_instructions is not None:
                    additional_info.care_instructions = care_instructions
                if materials is not None:
                    additional_info.materials = materials
                if cost is not None:
                    additional_info.cost = cost
            else:
                additional_info = AdditionalInfoForModelClothing(
                    model_clothing_id=model_id,
                    care_instructions=care_instructions,
                    materials=materials,
                    cost=cost,
                )
                db.session.add(additional_info)

            db.session.commit()
        else:
            print(f"Модель одежды с ID {model_id} не найдена.")


def delete_model_clothing(app, model_id):
    with app.app_context():
        clothing = ModelClothing.query.get(model_id)

        if clothing:
            # ModelPhoto
            photos = ModelPhoto.query.filter_by(model_clothing_id=model_id).all()
            for photo in photos:
                db.session.delete(photo)

            # AdditionalInfoForModelClothing
            additional_info = AdditionalInfoForModelClothing.query.get(model_id)
            if additional_info:
                db.session.delete(additional_info)

            # ModelPattern
            model_patterns = ModelPattern.query.filter_by(model_clothing_id=model_id).all()
            for model_pattern in model_patterns:
                db.session.delete(model_pattern)

            # ModelClothing
            db.session.delete(clothing)
            db.session.commit()

            print(f"Модель одежды удалена: ID - {model_id}, Название - {clothing.name}")
        else:
            print(f"Модель одежды с ID {model_id} не найдена.")
