Pasos para iniciar el servicio:

#Iniciar servicio
docker-compose up

#Crear usuario
docker-compose exec wearemo  bash
python wearemo/manage.py createsuperuser
#Para facilidad, se dejo creado un usuario llamado root, password root

#Documentacion en http://localhost:5050/swagger/
