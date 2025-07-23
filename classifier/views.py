# classifier/views.py - Versión completa con sistema de recomendaciones

import json
import os
import numpy as np
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage

# Mapeo de clases exacto de tu modelo
class_indices = {
    0: 'Abyssinian',
    1: 'Bengal',
    2: 'Birman',
    3: 'Bombay',
    4: 'British Shorthair',
    5: 'Egyptian Mau',
    6: 'Maine Coon',
    7: 'Persian',
    8: 'Ragdoll',
    9: 'Russian Blue',
    10: 'Siamese',
    11: 'Sphynx',
    12: 'American Bulldog',
    13: 'American Pit Bull Terrier',
    14: 'Basset Hound',
    15: 'Beagle',
    16: 'Boxer',
    17: 'Chihuahua',
    18: 'English Cocker Spaniel',
    19: 'English Setter',
    20: 'German Shorthaired Pointer',
    21: 'Great Pyrenees',
    22: 'Havanese',
    23: 'Japanese Chin',
    24: 'Keeshond',
    25: 'Leonberger',
    26: 'Miniature Pinscher',
    27: 'Newfoundland',
    28: 'Pomeranian',
    29: 'Pug',
    30: 'Saint Bernard',
    31: 'Samoyed',
    32: 'Scottish Terrier',
    33: 'Shiba Inu',
    34: 'Staffordshire Bull Terrier',
    35: 'Wheaten Terrier',
    36: 'Yorkshire Terrier'
}

razas_gatos = ['Abyssinian', 'Bengal', 'Birman', 'Bombay', 'British Shorthair', 'Egyptian Mau', 'Maine Coon', 
               'Persian', 'Ragdoll', 'Russian Blue', 'Siamese', 'Sphynx']
razas_perros = ['American Bulldog', 'American Pit Bull Terrier', 'Basset Hound', 'Beagle', 'Boxer', 'Chihuahua',
                'English Cocker Spaniel', 'English Setter', 'German Shorthaired Pointer', 'Great Pyrenees', 'Havanese',
                'Japanese Chin', 'Keeshond', 'Leonberger', 'Miniature Pinscher', 'Newfoundland', 'Pomeranian', 'Pug', 
                'Saint Bernard', 'Samoyed', 'Scottish Terrier', 'Shiba Inu', 'Staffordshire Bull Terrier', 
                'Wheaten Terrier', 'Yorkshire Terrier']

# Sistema de recomendaciones basado en características
BREED_CHARACTERISTICS = {
    # Gatos
    'Abyssinian': {'tamaño': 'mediano', 'energia': 'alta', 'cuidados': 'bajo', 'temperamento': 'activo', 'pelo': 'corto'},
    'Bengal': {'tamaño': 'mediano', 'energia': 'muy_alta', 'cuidados': 'medio', 'temperamento': 'jugueton', 'pelo': 'corto'},
    'Birman': {'tamaño': 'grande', 'energia': 'media', 'cuidados': 'alto', 'temperamento': 'tranquilo', 'pelo': 'largo'},
    'Bombay': {'tamaño': 'mediano', 'energia': 'media', 'cuidados': 'bajo', 'temperamento': 'cariñoso', 'pelo': 'corto'},
    'British Shorthair': {'tamaño': 'grande', 'energia': 'baja', 'cuidados': 'bajo', 'temperamento': 'tranquilo', 'pelo': 'corto'},
    'Egyptian Mau': {'tamaño': 'mediano', 'energia': 'alta', 'cuidados': 'bajo', 'temperamento': 'activo', 'pelo': 'corto'},
    'Maine Coon': {'tamaño': 'muy_grande', 'energia': 'media', 'cuidados': 'alto', 'temperamento': 'amigable', 'pelo': 'largo'},
    'Persian': {'tamaño': 'mediano', 'energia': 'baja', 'cuidados': 'muy_alto', 'temperamento': 'tranquilo', 'pelo': 'largo'},
    'Ragdoll': {'tamaño': 'grande', 'energia': 'baja', 'cuidados': 'medio', 'temperamento': 'docil', 'pelo': 'largo'},
    'Russian Blue': {'tamaño': 'mediano', 'energia': 'media', 'cuidados': 'bajo', 'temperamento': 'reservado', 'pelo': 'corto'},
    'Siamese': {'tamaño': 'mediano', 'energia': 'alta', 'cuidados': 'bajo', 'temperamento': 'vocal', 'pelo': 'corto'},
    'Sphynx': {'tamaño': 'mediano', 'energia': 'alta', 'cuidados': 'muy_alto', 'temperamento': 'extrovertido', 'pelo': 'sin_pelo'},

    # Perros
    'American Bulldog': {'tamaño': 'grande', 'energia': 'alta', 'cuidados': 'medio', 'temperamento': 'protector', 'pelo': 'corto'},
    'American Pit Bull Terrier': {'tamaño': 'mediano', 'energia': 'muy_alta', 'cuidados': 'medio', 'temperamento': 'energico', 'pelo': 'corto'},
    'Basset Hound': {'tamaño': 'mediano', 'energia': 'baja', 'cuidados': 'medio', 'temperamento': 'tranquilo', 'pelo': 'corto'},
    'Beagle': {'tamaño': 'mediano', 'energia': 'alta', 'cuidados': 'bajo', 'temperamento': 'amigable', 'pelo': 'corto'},
    'Boxer': {'tamaño': 'grande', 'energia': 'muy_alta', 'cuidados': 'bajo', 'temperamento': 'jugueton', 'pelo': 'corto'},
    'Chihuahua': {'tamaño': 'muy_pequeño', 'energia': 'media', 'cuidados': 'bajo', 'temperamento': 'alerta', 'pelo': 'corto'},
    'English Cocker Spaniel': {'tamaño': 'mediano', 'energia': 'alta', 'cuidados': 'alto', 'temperamento': 'amigable', 'pelo': 'largo'},
    'English Setter': {'tamaño': 'grande', 'energia': 'alta', 'cuidados': 'alto', 'temperamento': 'gentil', 'pelo': 'largo'},
    'German Shorthaired Pointer': {'tamaño': 'grande', 'energia': 'muy_alta', 'cuidados': 'bajo', 'temperamento': 'activo', 'pelo': 'corto'},
    'Great Pyrenees': {'tamaño': 'muy_grande', 'energia': 'media', 'cuidados': 'alto', 'temperamento': 'guardian', 'pelo': 'largo'},
    'Havanese': {'tamaño': 'pequeño', 'energia': 'media', 'cuidados': 'alto', 'temperamento': 'social', 'pelo': 'largo'},
    'Japanese Chin': {'tamaño': 'pequeño', 'energia': 'baja', 'cuidados': 'medio', 'temperamento': 'elegante', 'pelo': 'largo'},
    'Keeshond': {'tamaño': 'mediano', 'energia': 'media', 'cuidados': 'alto', 'temperamento': 'amigable', 'pelo': 'largo'},
    'Leonberger': {'tamaño': 'muy_grande', 'energia': 'media', 'cuidados': 'alto', 'temperamento': 'gentil', 'pelo': 'largo'},
    'Miniature Pinscher': {'tamaño': 'pequeño', 'energia': 'alta', 'cuidados': 'bajo', 'temperamento': 'alerta', 'pelo': 'corto'},
    'Newfoundland': {'tamaño': 'muy_grande', 'energia': 'baja', 'cuidados': 'alto', 'temperamento': 'gentil', 'pelo': 'largo'},
    'Pomeranian': {'tamaño': 'muy_pequeño', 'energia': 'media', 'cuidados': 'alto', 'temperamento': 'vivaz', 'pelo': 'largo'},
    'Pug': {'tamaño': 'pequeño', 'energia': 'baja', 'cuidados': 'bajo', 'temperamento': 'cariñoso', 'pelo': 'corto'},
    'Saint Bernard': {'tamaño': 'muy_grande', 'energia': 'baja', 'cuidados': 'alto', 'temperamento': 'gentil', 'pelo': 'largo'},
    'Samoyed': {'tamaño': 'grande', 'energia': 'alta', 'cuidados': 'muy_alto', 'temperamento': 'amigable', 'pelo': 'largo'},
    'Scottish Terrier': {'tamaño': 'pequeño', 'energia': 'media', 'cuidados': 'alto', 'temperamento': 'independiente', 'pelo': 'largo'},
    'Shiba Inu': {'tamaño': 'mediano', 'energia': 'media', 'cuidados': 'medio', 'temperamento': 'independiente', 'pelo': 'corto'},
    'Staffordshire Bull Terrier': {'tamaño': 'mediano', 'energia': 'alta', 'cuidados': 'bajo', 'temperamento': 'cariñoso', 'pelo': 'corto'},
    'Wheaten Terrier': {'tamaño': 'mediano', 'energia': 'alta', 'cuidados': 'alto', 'temperamento': 'amigable', 'pelo': 'largo'},
    'Yorkshire Terrier': {'tamaño': 'muy_pequeño', 'energia': 'media', 'cuidados': 'muy_alto', 'temperamento': 'valiente', 'pelo': 'largo'}
}

def calcular_similitud(raza1, raza2):
    """Calcular similitud entre dos razas basado en características"""
    if raza1 not in BREED_CHARACTERISTICS or raza2 not in BREED_CHARACTERISTICS:
        return 0
    
    chars1 = BREED_CHARACTERISTICS[raza1]
    chars2 = BREED_CHARACTERISTICS[raza2]
    
    # Pesos para diferentes características
    pesos = {
        'tamaño': 3,      # Más importante
        'energia': 2,     # Importante
        'cuidados': 2,    # Importante
        'temperamento': 1, # Menos importante
        'pelo': 1         # Menos importante
    }
    
    similitud = 0
    total_peso = 0
    
    for caracteristica, peso in pesos.items():
        if chars1[caracteristica] == chars2[caracteristica]:
            similitud += peso
        total_peso += peso
    
    return similitud / total_peso

def obtener_recomendaciones(raza_detectada, num_recomendaciones=3):
    """Obtener razas similares a la detectada"""
    print(f"🔍 Buscando recomendaciones para: {raza_detectada}")
    
    if raza_detectada not in BREED_CHARACTERISTICS:
        print(f"❌ Raza {raza_detectada} no encontrada en características")
        return []
    
    # Determinar si es gato o perro
    especie_detectada = 'gato' if raza_detectada in razas_gatos else 'perro'
    print(f"📋 Especie detectada: {especie_detectada}")
    
    # Filtrar razas de la misma especie
    razas_candidatas = razas_gatos if especie_detectada == 'gato' else razas_perros
    print(f"🎯 Evaluando {len(razas_candidatas)} razas candidatas")
    
    # Calcular similitudes
    similitudes = []
    for raza in razas_candidatas:
        if raza != raza_detectada:  # Excluir la raza detectada
            similitud = calcular_similitud(raza_detectada, raza)
            similitudes.append((raza, similitud))
            print(f"  {raza}: {similitud:.2f}")
    
    # Ordenar por similitud y tomar las mejores
    similitudes.sort(key=lambda x: x[1], reverse=True)
    
    recomendaciones = [raza for raza, _ in similitudes[:num_recomendaciones]]
    print(f"✅ Recomendaciones finales: {recomendaciones}")
    
    return recomendaciones

def obtener_caracteristicas_raza(raza):
    """Obtener características legibles de una raza"""
    if raza not in BREED_CHARACTERISTICS:
        return {}
    
    chars = BREED_CHARACTERISTICS[raza]
    
    # Mapear a descripciones legibles
    mapeos = {
        'tamaño': {
            'muy_pequeño': 'Muy pequeño',
            'pequeño': 'Pequeño', 
            'mediano': 'Mediano',
            'grande': 'Grande',
            'muy_grande': 'Muy grande'
        },
        'energia': {
            'baja': 'Energía baja',
            'media': 'Energía media',
            'alta': 'Energía alta',
            'muy_alta': 'Muy energético'
        },
        'cuidados': {
            'bajo': 'Cuidados simples',
            'medio': 'Cuidados moderados',
            'alto': 'Cuidados intensivos',
            'muy_alto': 'Cuidados muy intensivos'
        },
        'temperamento': {
            'tranquilo': 'Tranquilo',
            'activo': 'Activo',
            'jugueton': 'Juguetón',
            'cariñoso': 'Cariñoso',
            'amigable': 'Amigable',
            'protector': 'Protector',
            'gentil': 'Gentil',
            'independiente': 'Independiente',
            'energico': 'Enérgico',
            'alerta': 'Alerta',
            'docil': 'Dócil',
            'reservado': 'Reservado',
            'vocal': 'Vocal',
            'extrovertido': 'Extrovertido',
            'guardian': 'Guardián',
            'social': 'Social',
            'elegante': 'Elegante',
            'vivaz': 'Vivaz',
            'valiente': 'Valiente'
        },
        'pelo': {
            'corto': 'Pelo corto',
            'largo': 'Pelo largo',
            'sin_pelo': 'Sin pelo'
        }
    }
    
    resultado = {}
    for categoria, valor in chars.items():
        if categoria in mapeos and valor in mapeos[categoria]:
            resultado[categoria] = mapeos[categoria][valor]
    
    return resultado


# Variables globales
model = None
breeds_info = {}

# Cargar modelo y datos
try:
    # Cargar JSON
    json_path = os.path.join(settings.BASE_DIR, 'breeds_info.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            breeds_info = json.load(f)
        print(f"✅ JSON cargado: {len(breeds_info)} especies")
    else:
        print("❌ breeds_info.json no encontrado")
    
    # Cargar modelo
    model_path = os.path.join(settings.BASE_DIR, 'inception_model2.keras')
    if os.path.exists(model_path):
        try:
            from tensorflow.keras.models import load_model
            from tensorflow.keras.preprocessing.image import img_to_array, load_img
            
            model = load_model(model_path)
            print("✅ Modelo cargado exitosamente!")
            print(f"📊 Input shape: {model.input_shape}")
            print(f"📊 Output shape: {model.output_shape}")
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            model = None
    else:
        print("❌ inception_model2.keras no encontrado")
        
except Exception as e:
    print(f"❌ Error general: {e}")

print("=== FIN INICIALIZACIÓN ===")

def prepare_image(image_path):
    """Preprocesar la imagen para que sea compatible con el modelo"""
    try:
        from tensorflow.keras.preprocessing.image import img_to_array, load_img
        
        image = load_img(image_path, target_size=(299, 299))
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)
        image /= 255.0
        return image
    except Exception as e:
        print(f"Error preparando imagen: {e}")
        return None

def obtener_info_raza(especie, raza):
    """Obtener información de la raza desde el JSON"""
    try:
        info_raza = breeds_info.get(especie, {}).get(raza, {})
        return info_raza
    except Exception as e:
        print(f"Error obteniendo info de raza: {e}")
        return {}

def home(request):
    return render(request, 'classifier/home.html')

def classifier_view(request):
    print(f"\n🔄 classifier_view - Método: {request.method}")
    
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            # Obtener archivo
            image_file = request.FILES['image']
            print(f"📂 Procesando: {image_file.name} ({image_file.size} bytes)")
            
            # Verificar modelo disponible
            if model is None:
                print("❌ Modelo no disponible")
                context = {
                    'success': False,
                    'message': 'Error: Modelo no disponible. Verifica que TensorFlow esté instalado y el modelo sea compatible.'
                }
                return render(request, 'classifier/classifier.html', context)
            
            # Guardar imagen temporalmente
            try:
                filepath = default_storage.save('temp_images/' + image_file.name, image_file)
                image_path = os.path.join(settings.MEDIA_ROOT, filepath)
                image_url = f"{settings.MEDIA_URL}{filepath}"  # URL para mostrar en el template
                print(f"💾 Imagen guardada en: {image_path}")
                print(f"🌐 URL de imagen: {image_url}")
                
                # Preparar imagen para predicción
                processed_image = prepare_image(image_path)
                if processed_image is None:
                    raise Exception("Error procesando la imagen")
                
                # Realizar predicción
                print("🤖 Realizando predicción...")
                prediction = model.predict(processed_image)
                predicted_class = np.argmax(prediction[0])
                confidence = float(prediction[0][predicted_class])
                
                print(f"🎯 Clase predicha: {predicted_class}")
                print(f"📊 Confianza: {confidence:.3f}")
                
                # Verificar confianza mínima
                if confidence >= 0.90:
                    breed = class_indices[predicted_class]
                    print(f"✅ Raza detectada: {breed}")
                    
                    # Determinar especie
                    if breed in razas_gatos:
                        especie = 'gato'
                    elif breed in razas_perros:
                        especie = 'perro'
                    else:
                        especie = 'desconocido'
                    
                    # Obtener información de la raza
                    info_raza = obtener_info_raza(especie, breed)
                    
                    # Obtener recomendaciones
                    
                    recomendaciones = obtener_recomendaciones(breed, 3)
                    caracteristicas_detectada = obtener_caracteristicas_raza(breed)
                    
                    
                    
                    # Obtener info de razas recomendadas
                    recomendaciones_info = []
                    for raza_rec in recomendaciones:
                        especie_rec = 'gato' if raza_rec in razas_gatos else 'perro'
                        info_rec = obtener_info_raza(especie_rec, raza_rec)
                        caracteristicas_rec = obtener_caracteristicas_raza(raza_rec)
                        recomendaciones_info.append({
                            'nombre': raza_rec,
                            'especie': especie_rec,
                            'info': info_rec,
                            'caracteristicas': caracteristicas_rec
                        })
                        print(f"  ✅ {raza_rec} ({especie_rec}) - Características: {caracteristicas_rec}")
                    
                    print(f"📋 Total recomendaciones procesadas: {len(recomendaciones_info)}")
                    
                    context = {
                        'success': True,
                        'breed_name': breed,
                        'especie': especie,
                        'confidence': confidence * 100,
                        'breed_info': info_raza,
                        'image_url': image_url,
                        'caracteristicas': caracteristicas_detectada,
                        'recomendaciones': recomendaciones_info
                    }
                    
                    
                else:
                    print(f"❌ Confianza insuficiente: {confidence:.3f}")
                    context = {
                        'success': False,
                        'message': 'No se detectó la raza de la mascota con suficiente confianza.',
                        'confidence': confidence * 100,
                        'image_url': image_url  # Mostrar imagen incluso si falla
                    }
                
                # NO eliminar archivo temporal hasta después de mostrar la imagen
                # Solo lo eliminamos al final
                
                return render(request, 'classifier/classifier.html', context)
                
            except Exception as e:
                print(f"❌ Error procesando imagen: {e}")
                context = {
                    'success': False,
                    'message': f'Error procesando la imagen: {str(e)}'
                }
                return render(request, 'classifier/classifier.html', context)
                
        except Exception as e:
            print(f"❌ Error general: {e}")
            import traceback
            traceback.print_exc()
            context = {
                'success': False,
                'message': f'Error: {str(e)}'
            }
            return render(request, 'classifier/classifier.html', context)
    
    print("📄 Mostrando página inicial")
    return render(request, 'classifier/classifier.html')

def quiz_view(request):
    if request.method == 'POST':
        # Procesar respuestas del quiz
        respuestas = {}
        for pregunta in QUIZ_QUESTIONS:
            respuesta = request.POST.get(pregunta['id'])
            if respuesta:
                respuestas[pregunta['id']] = respuesta
        
        print(f"📝 Respuestas recibidas: {respuestas}")
        
        if len(respuestas) >= len(QUIZ_QUESTIONS):
            # Calcular recomendaciones
            top_razas, perfil_usuario = calcular_puntuacion_quiz(respuestas)
            
            # Obtener información detallada de las razas recomendadas
            recomendaciones_detalladas = []
            for resultado in top_razas:
                raza = resultado['raza']
                especie = resultado['especie']
                info_raza = obtener_info_raza(especie, raza)
                explicacion = explicar_recomendacion(raza, perfil_usuario)
                
                recomendaciones_detalladas.append({
                    'raza': raza,
                    'especie': especie,
                    'puntuacion': resultado['puntuacion'],
                    'info': info_raza,
                    'explicacion': explicacion,
                    'caracteristicas': obtener_caracteristicas_raza(raza)
                })
            
            context = {
                'resultados': True,
                'recomendaciones': recomendaciones_detalladas,
                'perfil_usuario': perfil_usuario
            }
            
            return render(request, 'classifier/quiz.html', context)
        else:
            # Faltan respuestas
            context = {
                'error': 'Por favor responde todas las preguntas',
                'preguntas': QUIZ_QUESTIONS
            }
            return render(request, 'classifier/quiz.html', context)
    
    # GET request - mostrar quiz
    context = {
        'preguntas': QUIZ_QUESTIONS
    }
    return render(request, 'classifier/quiz.html', context)

def calculator_view(request):
    opciones = obtener_opciones_calculadora()
    
    if request.method == 'POST':
        accion = request.POST.get('accion', 'calcular')
        
        if accion == 'calcular':
            # Calcular para una sola raza
            raza_seleccionada = request.POST.get('raza')
            if not raza_seleccionada or raza_seleccionada not in BREED_CHARACTERISTICS:
                context = {
                    'error': 'Por favor selecciona una raza válida',
                    'opciones': opciones
                }
                return render(request, 'classifier/calculator.html', context)
            
            # Obtener opciones del usuario
            opciones_usuario = {
                'tipo_adopcion': request.POST.get('tipo_adopcion', 'refugio'),
                'nivel_accesorios': request.POST.get('nivel_accesorios', 'basicos'),
                'tipo_comida': request.POST.get('tipo_comida', 'economica'),
                'nivel_cuidados': request.POST.get('nivel_cuidados', 'basico'),
                'plan_salud': request.POST.get('plan_salud', 'basico'),
                'fondo_emergencia': request.POST.get('fondo_emergencia', 'moderado')
            }
            
            # Calcular gastos
            gastos = calcular_gastos_raza(raza_seleccionada, opciones_usuario)
            
            if gastos:
                especie = 'gato' if raza_seleccionada in razas_gatos else 'perro'
                info_raza = obtener_info_raza(especie, raza_seleccionada)
                
                context = {
                    'resultado': True,
                    'raza': raza_seleccionada,
                    'especie': especie,
                    'gastos': gastos,
                    'info_raza': info_raza,
                    'opciones_usuario': opciones_usuario,
                    'opciones': opciones
                }
            else:
                context = {
                    'error': 'Error calculando gastos para la raza seleccionada',
                    'opciones': opciones
                }
        
        elif accion == 'comparar':
            # Comparar múltiples razas
            razas_comparar = request.POST.getlist('razas_comparar')
            if len(razas_comparar) < 2:
                context = {
                    'error': 'Selecciona al menos 2 razas para comparar',
                    'opciones': opciones
                }
                return render(request, 'classifier/calculator.html', context)
            
            # Usar las mismas opciones para todas las razas
            opciones_usuario = {
                'tipo_adopcion': request.POST.get('tipo_adopcion', 'refugio'),
                'nivel_accesorios': request.POST.get('nivel_accesorios', 'basicos'),
                'tipo_comida': request.POST.get('tipo_comida', 'economica'),
                'nivel_cuidados': request.POST.get('nivel_cuidados', 'basico'),
                'plan_salud': request.POST.get('plan_salud', 'basico'),
                'fondo_emergencia': request.POST.get('fondo_emergencia', 'moderado')
            }
            
            comparacion = comparar_razas(razas_comparar, opciones_usuario)
            
            context = {
                'comparacion': True,
                'resultados_comparacion': comparacion,
                'opciones_usuario': opciones_usuario,
                'opciones': opciones
            }
        
        return render(request, 'classifier/calculator.html', context)
    
    # GET request - mostrar formulario
    context = {
        'opciones': opciones
    }
    return render(request, 'classifier/calculator.html', context)

################33 quiz
# Preguntas del quiz
QUIZ_QUESTIONS = [
    {
        'id': 'vivienda',
        'pregunta': '¿Dónde vives?',
        'opciones': [
            {'valor': 'apartamento_pequeño', 'texto': 'Apartamento pequeño'},
            {'valor': 'apartamento_grande', 'texto': 'Apartamento grande'},
            {'valor': 'casa_sin_jardin', 'texto': 'Casa sin jardín'},
            {'valor': 'casa_con_jardin', 'texto': 'Casa con jardín grande'}
        ]
    },
    {
        'id': 'tiempo_ejercicio',
        'pregunta': '¿Cuánto tiempo puedes dedicar al ejercicio diario?',
        'opciones': [
            {'valor': 'menos_30min', 'texto': 'Menos de 30 minutos'},
            {'valor': '30_60min', 'texto': '30-60 minutos'},
            {'valor': '1_2horas', 'texto': '1-2 horas'},
            {'valor': 'mas_2horas', 'texto': 'Más de 2 horas'}
        ]
    },
    {
        'id': 'experiencia',
        'pregunta': '¿Cuál es tu experiencia con mascotas?',
        'opciones': [
            {'valor': 'principiante', 'texto': 'Soy principiante'},
            {'valor': 'intermedio', 'texto': 'Tengo algo de experiencia'},
            {'valor': 'experto', 'texto': 'Soy muy experimentado'}
        ]
    },
    {
        'id': 'tiempo_cuidados',
        'pregunta': '¿Cuánto tiempo puedes dedicar a cuidados (aseo, cepillado)?',
        'opciones': [
            {'valor': 'minimo', 'texto': 'Mínimo (5-10 min/día)'},
            {'valor': 'moderado', 'texto': 'Moderado (15-30 min/día)'},
            {'valor': 'intensivo', 'texto': 'Intensivo (30+ min/día)'}
        ]
    },
    {
        'id': 'preferencia_animal',
        'pregunta': '¿Prefieres gatos o perros?',
        'opciones': [
            {'valor': 'gatos', 'texto': 'Prefiero gatos'},
            {'valor': 'perros', 'texto': 'Prefiero perros'},
            {'valor': 'ambos', 'texto': 'Me gustan ambos'}
        ]
    },
    {
        'id': 'tamaño_preferido',
        'pregunta': '¿Qué tamaño de mascota prefieres?',
        'opciones': [
            {'valor': 'muy_pequeño', 'texto': 'Muy pequeño (menos de 5kg)'},
            {'valor': 'pequeño', 'texto': 'Pequeño (5-15kg)'},
            {'valor': 'mediano', 'texto': 'Mediano (15-30kg)'},
            {'valor': 'grande', 'texto': 'Grande (30kg+)'},
            {'valor': 'sin_preferencia', 'texto': 'Sin preferencia'}
        ]
    },
    {
        'id': 'nivel_energia',
        'pregunta': '¿Qué nivel de energía prefieres en tu mascota?',
        'opciones': [
            {'valor': 'baja', 'texto': 'Tranquila y relajada'},
            {'valor': 'media', 'texto': 'Moderadamente activa'},
            {'valor': 'alta', 'texto': 'Muy activa y juguetona'}
        ]
    },
    {
        'id': 'ninos_casa',
        'pregunta': '¿Hay niños en casa?',
        'opciones': [
            {'valor': 'no', 'texto': 'No hay niños'},
            {'valor': 'si_pequeños', 'texto': 'Sí, niños pequeños (0-8 años)'},
            {'valor': 'si_mayores', 'texto': 'Sí, niños mayores (9+ años)'}
        ]
    },
    {
        'id': 'otras_mascotas',
        'pregunta': '¿Tienes otras mascotas?',
        'opciones': [
            {'valor': 'no', 'texto': 'No tengo otras mascotas'},
            {'valor': 'si_gatos', 'texto': 'Sí, tengo gatos'},
            {'valor': 'si_perros', 'texto': 'Sí, tengo perros'},
            {'valor': 'si_ambos', 'texto': 'Sí, tengo gatos y perros'}
        ]
    }
]

def calcular_puntuacion_quiz(respuestas):
    """Calcular qué razas son más compatibles basándose en las respuestas del quiz"""
    
    print(f"📝 Calculando compatibilidad para respuestas: {respuestas}")
    
    # Mapear respuestas a características preferidas
    perfil_usuario = analizar_perfil_usuario(respuestas)
    print(f"👤 Perfil del usuario: {perfil_usuario}")
    
    # Filtrar razas según preferencia de animal
    razas_evaluar = []
    if perfil_usuario['preferencia_animal'] == 'gatos':
        razas_evaluar = razas_gatos
    elif perfil_usuario['preferencia_animal'] == 'perros':
        razas_evaluar = razas_perros
    else:  # ambos
        razas_evaluar = razas_gatos + razas_perros
    
    # Calcular puntuación para cada raza
    puntuaciones = []
    for raza in razas_evaluar:
        if raza in BREED_CHARACTERISTICS:
            puntuacion = calcular_compatibilidad_raza(raza, perfil_usuario)
            especie = 'gato' if raza in razas_gatos else 'perro'
            puntuaciones.append({
                'raza': raza,
                'especie': especie,
                'puntuacion': puntuacion,
                'caracteristicas': BREED_CHARACTERISTICS[raza]
            })
            print(f"  {raza}: {puntuacion:.2f}")
    
    # Ordenar por puntuación y tomar top 3
    puntuaciones.sort(key=lambda x: x['puntuacion'], reverse=True)
    top_razas = puntuaciones[:3]
    
    print(f"🏆 Top 3 razas: {[r['raza'] for r in top_razas]}")
    
    return top_razas, perfil_usuario

def analizar_perfil_usuario(respuestas):
    """Convertir respuestas del quiz a perfil de características"""
    perfil = {
        'tamaño_preferido': 'sin_preferencia',
        'energia_preferida': 'media',
        'cuidados_disponibles': 'medio',
        'experiencia': 'intermedio',
        'espacio': 'medio',
        'preferencia_animal': 'ambos'
    }
    
    # Mapear vivienda a espacio disponible
    vivienda = respuestas.get('vivienda', '')
    if vivienda in ['apartamento_pequeño']:
        perfil['espacio'] = 'pequeño'
        perfil['tamaño_preferido'] = 'pequeño'
    elif vivienda in ['casa_con_jardin']:
        perfil['espacio'] = 'grande'
    
    # Mapear tiempo de ejercicio a energía preferida
    tiempo_ejercicio = respuestas.get('tiempo_ejercicio', '')
    if tiempo_ejercicio == 'menos_30min':
        perfil['energia_preferida'] = 'baja'
    elif tiempo_ejercicio in ['1_2horas', 'mas_2horas']:
        perfil['energia_preferida'] = 'alta'
    
    # Mapear tiempo de cuidados
    tiempo_cuidados = respuestas.get('tiempo_cuidados', '')
    if tiempo_cuidados == 'minimo':
        perfil['cuidados_disponibles'] = 'bajo'
    elif tiempo_cuidados == 'intensivo':
        perfil['cuidados_disponibles'] = 'alto'
    
    # Otras preferencias directas
    perfil['experiencia'] = respuestas.get('experiencia', 'intermedio')
    perfil['preferencia_animal'] = respuestas.get('preferencia_animal', 'ambos')
    
    tamaño_pref = respuestas.get('tamaño_preferido', 'sin_preferencia')
    if tamaño_pref != 'sin_preferencia':
        perfil['tamaño_preferido'] = tamaño_pref
    
    energia_pref = respuestas.get('nivel_energia', 'media')
    perfil['energia_preferida'] = energia_pref
    
    return perfil

def calcular_compatibilidad_raza(raza, perfil_usuario):
    """Calcular qué tan compatible es una raza con el perfil del usuario"""
    caracteristicas_raza = BREED_CHARACTERISTICS[raza]
    puntuacion = 0
    
    # Puntuación por tamaño (peso: 3)
    if perfil_usuario['tamaño_preferido'] == 'sin_preferencia':
        puntuacion += 2  # Sin penalización
    elif perfil_usuario['tamaño_preferido'] == caracteristicas_raza['tamaño']:
        puntuacion += 3
    elif abs(['muy_pequeño', 'pequeño', 'mediano', 'grande', 'muy_grande'].index(perfil_usuario['tamaño_preferido']) - 
             ['muy_pequeño', 'pequeño', 'mediano', 'grande', 'muy_grande'].index(caracteristicas_raza['tamaño'])) <= 1:
        puntuacion += 1  # Tamaños similares
    
    # Puntuación por energía (peso: 3)
    energia_usuario = perfil_usuario['energia_preferida']
    energia_raza = caracteristicas_raza['energia']
    
    if energia_usuario == energia_raza:
        puntuacion += 3
    elif (energia_usuario == 'media' and energia_raza in ['baja', 'alta']) or \
         (energia_raza == 'media' and energia_usuario in ['baja', 'alta']):
        puntuacion += 1
    
    # Puntuación por cuidados (peso: 2)
    cuidados_usuario = perfil_usuario['cuidados_disponibles']
    cuidados_raza = caracteristicas_raza['cuidados']
    
    if cuidados_usuario == 'alto' and cuidados_raza in ['bajo', 'medio', 'alto', 'muy_alto']:
        puntuacion += 2  # Puede manejar cualquier nivel
    elif cuidados_usuario == 'medio' and cuidados_raza in ['bajo', 'medio']:
        puntuacion += 2
    elif cuidados_usuario == 'bajo' and cuidados_raza == 'bajo':
        puntuacion += 2
    elif cuidados_usuario == 'medio' and cuidados_raza == 'alto':
        puntuacion += 1  # Puede funcionar pero será exigente
    
    # Puntuación por experiencia (peso: 1)
    experiencia = perfil_usuario['experiencia']
    if experiencia == 'experto':
        puntuacion += 1  # Puede manejar cualquier raza
    elif experiencia == 'intermedio' and cuidados_raza != 'muy_alto':
        puntuacion += 1
    elif experiencia == 'principiante' and cuidados_raza == 'bajo':
        puntuacion += 1
    
    return puntuacion / 9  # Normalizar a 0-1

def explicar_recomendacion(raza, perfil_usuario):
    """Generar explicación de por qué se recomienda esta raza"""
    caracteristicas = BREED_CHARACTERISTICS[raza]
    razones = []
    
    # Analizar compatibilidades
    if perfil_usuario['energia_preferida'] == caracteristicas['energia']:
        energia_text = {
            'baja': 'tranquila y relajada',
            'media': 'moderadamente activa', 
            'alta': 'muy activa',
            'muy_alta': 'extremadamente energética'
        }
        razones.append(f"Es {energia_text.get(caracteristicas['energia'], 'de energía media')}, como prefieres")
    
    if perfil_usuario['cuidados_disponibles'] == 'alto' and caracteristicas['cuidados'] in ['alto', 'muy_alto']:
        razones.append("Requiere cuidados intensivos que estás dispuesto a dar")
    elif perfil_usuario['cuidados_disponibles'] == 'bajo' and caracteristicas['cuidados'] == 'bajo':
        razones.append("Requiere cuidados mínimos, perfecto para tu estilo de vida")
    
    if perfil_usuario['tamaño_preferido'] == caracteristicas['tamaño']:
        tamaño_text = {
            'muy_pequeño': 'muy pequeño',
            'pequeño': 'pequeño',
            'mediano': 'mediano',
            'grande': 'grande',
            'muy_grande': 'muy grande'
        }
        razones.append(f"Su tamaño {tamaño_text.get(caracteristicas['tamaño'], 'mediano')} coincide con tus preferencias")
    
    if not razones:
        razones.append("Es una buena opción equilibrada para tu estilo de vida")
    
    return razones


############## calculadora:
# Datos de costos base por categorías (en USD, ajustables por región)
COSTOS_BASE = {
    'adopcion': {
        'refugio': {'min': 0, 'max': 10},
        'criador': {'min': 500, 'max': 3000},
        'tienda': {'min': 800, 'max': 2500}
    },
    'accesorios_iniciales': {
        'basicos': {'min': 20, 'max': 40},
        'premium': {'min': 300, 'max': 800}
    },
    'comida_mensual': {
        # Por tamaño de mascota
        'muy_pequeño': {'economica': 15, 'premium': 40},
        'pequeño': {'economica': 25, 'premium': 60},
        'mediano': {'economica': 40, 'premium': 90},
        'grande': {'economica': 60, 'premium': 130},
        'muy_grande': {'economica': 80, 'premium': 170}
    },
    'veterinario_anual': {
        # Gastos vet básicos anuales
        'basico': {'min': 100, 'max': 500},
        'completo': {'min': 500, 'max': 1200},
        'premium': {'min': 1000, 'max': 2000}
    },
    'cuidados_mensuales': {
        # Según nivel de cuidados de la raza
        'bajo': {'basico': 10, 'completo': 30},
        'medio': {'basico': 20, 'completo': 50},
        'alto': {'basico': 40, 'completo': 80},
        'muy_alto': {'basico': 60, 'completo': 120}
    },
    'emergencias_anuales': {
        # Fondo de emergencias recomendado
        'conservador': 250,
        'moderado': 1000,
        'completo': 2000
    }
}

# Multiplicadores según características de la raza
MULTIPLICADORES_RAZA = {
    'salud': {
        # Razas con más riesgos de salud = mayor costo vet
        'bajo_riesgo': 0.8,
        'riesgo_normal': 1.0,
        'alto_riesgo': 1.3
    },
    'cuidados': {
        # Nivel de cuidados afecta gastos de grooming
        'bajo': 0.7,
        'medio': 1.0,
        'alto': 1.5,
        'muy_alto': 2.0
    },
    'tamaño': {
        # Tamaño afecta comida y algunos tratamientos
        'muy_pequeño': 0.6,
        'pequeño': 0.8,
        'mediano': 1.0,
        'grande': 1.3,
        'muy_grande': 1.6
    }
}

# Clasificación de razas por riesgo de salud (basado en riesgos conocidos)
RIESGOS_SALUD_RAZAS = {
    'bajo_riesgo': ['Russian Blue', 'Havanese', 'Beagle', 'Shiba Inu'],
    'alto_riesgo': ['Persian', 'Pug', 'Bulldog', 'Sphynx', 'Great Pyrenees', 'Saint Bernard'],
    # El resto se considera 'riesgo_normal'
}

def calcular_gastos_raza(raza, opciones_usuario):
    """Calcular gastos estimados para una raza específica"""
    
    if raza not in BREED_CHARACTERISTICS:
        return None
    
    print(f"💰 Calculando gastos para {raza} con opciones: {opciones_usuario}")
    
    caracteristicas = BREED_CHARACTERISTICS[raza]
    gastos = {}
    
    # 1. Costos iniciales (una sola vez)
    gastos['adopcion'] = calcular_costo_adopcion(opciones_usuario.get('tipo_adopcion', 'refugio'))
    gastos['accesorios'] = calcular_costo_accesorios(opciones_usuario.get('nivel_accesorios', 'basicos'))
    
    # 2. Costos mensuales
    gastos['comida_mensual'] = calcular_costo_comida(caracteristicas['tamaño'], opciones_usuario.get('tipo_comida', 'economica'))
    gastos['cuidados_mensuales'] = calcular_costo_cuidados(caracteristicas['cuidados'], opciones_usuario.get('nivel_cuidados', 'basico'))
    
    # 3. Costos anuales
    gastos['veterinario_anual'] = calcular_costo_veterinario(raza, opciones_usuario.get('plan_salud', 'basico'))
    gastos['emergencias_anuales'] = COSTOS_BASE['emergencias_anuales'][opciones_usuario.get('fondo_emergencia', 'moderado')]
    
    # 4. Calcular totales
    gastos['inicial_total'] = gastos['adopcion'] + gastos['accesorios']
    gastos['mensual_total'] = gastos['comida_mensual'] + gastos['cuidados_mensuales']
    gastos['anual_total'] = (gastos['mensual_total'] * 12) + gastos['veterinario_anual'] + gastos['emergencias_anuales']
    
    # 5. Proyección de vida completa
    esperanza_vida = extraer_años_vida(raza)
    gastos['vida_total'] = gastos['inicial_total'] + (gastos['anual_total'] * esperanza_vida)
    gastos['esperanza_vida'] = esperanza_vida
    
    print(f"💵 Gastos calculados - Anual: {gastos['anual_total']:.0f}, Vida: ${gastos['vida_total']:.0f}")
    
    return gastos

def calcular_costo_adopcion(tipo):
    """Calcular costo de adopción según tipo"""
    costos = COSTOS_BASE['adopcion'][tipo]
    return (costos['min'] + costos['max']) / 2

def calcular_costo_accesorios(nivel):
    """Calcular costo de accesorios iniciales"""
    costos = COSTOS_BASE['accesorios_iniciales'][nivel]
    return (costos['min'] + costos['max']) / 2

def calcular_costo_comida(tamaño, tipo_comida):
    """Calcular costo mensual de comida"""
    return COSTOS_BASE['comida_mensual'][tamaño][tipo_comida]

def calcular_costo_cuidados(nivel_cuidados, tipo_servicio):
    """Calcular costo mensual de cuidados"""
    return COSTOS_BASE['cuidados_mensuales'][nivel_cuidados][tipo_servicio]

def calcular_costo_veterinario(raza, plan):
    """Calcular costo veterinario anual con multiplicador por raza"""
    costos_base = COSTOS_BASE['veterinario_anual'][plan]
    costo_promedio = (costos_base['min'] + costos_base['max']) / 2
    
    # Aplicar multiplicador según riesgo de salud
    if raza in RIESGOS_SALUD_RAZAS['bajo_riesgo']:
        multiplicador = MULTIPLICADORES_RAZA['salud']['bajo_riesgo']
    elif raza in RIESGOS_SALUD_RAZAS['alto_riesgo']:
        multiplicador = MULTIPLICADORES_RAZA['salud']['alto_riesgo']
    else:
        multiplicador = MULTIPLICADORES_RAZA['salud']['riesgo_normal']
    
    return costo_promedio * multiplicador

def extraer_años_vida(raza):
    """Extraer esperanza de vida en años del JSON de información"""
    try:
        especie = 'gato' if raza in razas_gatos else 'perro'
        info_raza = obtener_info_raza(especie, raza)
        esperanza_texto = info_raza.get('esperanza_de_vida', '12 años')
        
        # Extraer números del texto (ej: "10-15 años" -> 12.5)
        import re
        numeros = re.findall(r'\d+', esperanza_texto)
        if len(numeros) >= 2:
            return (int(numeros[0]) + int(numeros[1])) / 2
        elif len(numeros) == 1:
            return int(numeros[0])
        else:
            return 12  # Valor por defecto
    except:
        return 12

def comparar_razas(razas_lista, opciones_usuario):
    """Comparar gastos entre múltiples razas"""
    comparacion = []
    
    for raza in razas_lista:
        gastos = calcular_gastos_raza(raza, opciones_usuario)
        if gastos:
            especie = 'gato' if raza in razas_gatos else 'perro'
            comparacion.append({
                'raza': raza,
                'especie': especie,
                'gastos': gastos,
                'caracteristicas': BREED_CHARACTERISTICS.get(raza, {})
            })
    
    # Ordenar por costo anual
    comparacion.sort(key=lambda x: x['gastos']['anual_total'])
    
    return comparacion

def obtener_opciones_calculadora():
    """Obtener todas las opciones disponibles para la calculadora"""
    return {
        'tipos_adopcion': [
            {'valor': 'refugio', 'texto': 'Refugio/Adopción (50-200)', 'descripcion': 'Adoptar de refugios locales'},
            {'valor': 'criador', 'texto': 'Criador Responsable (500-3000)', 'descripcion': 'Comprar de criador certificado'},
            {'valor': 'tienda', 'texto': 'Tienda de Mascotas (800-2500)', 'descripcion': 'Comprar en tienda especializada'}
        ],
        'niveles_accesorios': [
            {'valor': 'basicos', 'texto': 'Básicos (100-300)', 'descripcion': 'Cama, comederos, juguetes básicos'},
            {'valor': 'premium', 'texto': 'Premium (300-800)', 'descripcion': 'Accesorios de alta calidad'}
        ],
        'tipos_comida': [
            {'valor': 'economica', 'texto': 'Económica', 'descripcion': 'Alimento comercial estándar'},
            {'valor': 'premium', 'texto': 'Premium', 'descripcion': 'Alimento super premium/natural'}
        ],
        'niveles_cuidados': [
            {'valor': 'basico', 'texto': 'Básico', 'descripcion': 'Cuidados en casa'},
            {'valor': 'completo', 'texto': 'Profesional', 'descripcion': 'Servicios profesionales regulares'}
        ],
        'planes_salud': [
            {'valor': 'basico', 'texto': 'Básico (200-500/año)', 'descripcion': 'Vacunas y chequeos básicos'},
            {'valor': 'completo', 'texto': 'Completo (500-1200/año)', 'descripcion': 'Incluye análisis y tratamientos'},
            {'valor': 'premium', 'texto': 'Premium (1000-2000/año)', 'descripcion': 'Cobertura integral + seguros'}
        ],
        'fondos_emergencia': [
            {'valor': 'conservador', 'texto': 'Conservador (500/año)', 'descripcion': 'Para emergencias menores'},
            {'valor': 'moderado', 'texto': 'Moderado (1000/año)', 'descripcion': 'Recomendado para la mayoría'},
            {'valor': 'completo', 'texto': 'Completo (2000/año)', 'descripcion': 'Para máxima tranquilidad'}
        ],
        'todas_razas': sorted(list(BREED_CHARACTERISTICS.keys()))
    }