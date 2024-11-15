# -*- coding: utf-8 -*-
"""CNN_Kelompok 5.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1FMf6I2Iyb9a8M2KO_gBPHvzx5hgNhCwi
"""

import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import layers, models, Input, Model
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

# Fungsi Preprocessing: Enhancement menggunakan CLAHE
def apply_clahe(image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)

# Fungsi untuk memuat dan memproses gambar
def load_and_preprocess_images(image_dir):
    images = []
    labels = []
    for label in os.listdir(image_dir):
        label_dir = os.path.join(image_dir, label)
        if os.path.isdir(label_dir):
            for img_file in os.listdir(label_dir):
                img_path = os.path.join(label_dir, img_file)
                image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Membaca gambar dalam mode grayscale
                enhanced_image = apply_clahe(image)
                resized_image = cv2.resize(enhanced_image, (128, 128))  # Resize image sesuai kebutuhan
                images.append(resized_image)
                labels.append(label)
    images = np.array(images)
    images = np.expand_dims(images, axis=-1)  # Tambahkan dimensi channel (1) untuk gambar grayscale
    labels = np.array(labels)
    return images, labels

# Direktori data
image_dir = "data"  # Sesuaikan dengan direktori data kamu

# Load dan preprocess gambar
images, labels = load_and_preprocess_images(image_dir)

# Mengubah label string menjadi label numerik
label_encoder = LabelEncoder()
labels_encoded = label_encoder.fit_transform(labels)

# Split data menjadi training dan testing
X_train, X_test, y_train, y_test = train_test_split(images, labels_encoded, test_size=0.2, random_state=42)

# Konversi label ke bentuk one-hot encoding
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)

# Augmentasi (Zoom, Rotation, Flip Horizontal, dan Shear)
train_datagen = ImageDataGenerator(
    zoom_range=0.2,
    rotation_range=20,
    horizontal_flip=True,
    shear_range=0.2
)
train_datagen.fit(X_train)

# Fungsi untuk membuat blok Inception
def inception_module(x, filters):
    # 1x1 convolution
    conv1 = layers.Conv2D(filters[0], (1, 1), padding='same', activation='relu')(x)

    # 3x3 convolution
    conv3 = layers.Conv2D(filters[1], (1, 1), padding='same', activation='relu')(x)
    conv3 = layers.Conv2D(filters[2], (3, 3), padding='same', activation='relu')(conv3)

    # 5x5 convolution
    conv5 = layers.Conv2D(filters[3], (1, 1), padding='same', activation='relu')(x)
    conv5 = layers.Conv2D(filters[4], (5, 5), padding='same', activation='relu')(conv5)

    # 3x3 max pooling
    pool = layers.MaxPooling2D((3, 3), strides=(1, 1), padding='same')(x)
    pool = layers.Conv2D(filters[5], (1, 1), padding='same', activation='relu')(pool)

    # Concatenate all filters
    output = layers.concatenate([conv1, conv3, conv5, pool], axis=-1)
    return output

# Arsitektur Model Inception
input_img = Input(shape=(128, 128, 1))

x = layers.Conv2D(64, (7, 7), strides=(2, 2), padding='same', activation='relu')(input_img)
x = layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)

x = layers.Conv2D(64, (1, 1), padding='same', activation='relu')(x)
x = layers.Conv2D(192, (3, 3), padding='same', activation='relu')(x)
x = layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)

# Inception modules
x = inception_module(x, [64, 96, 128, 16, 32, 32])
x = inception_module(x, [128, 128, 192, 32, 96, 64])
x = layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)

x = inception_module(x, [192, 96, 208, 16, 48, 64])
x = inception_module(x, [160, 112, 224, 24, 64, 64])
x = inception_module(x, [128, 128, 256, 24, 64, 64])
x = inception_module(x, [112, 144, 288, 32, 64, 64])
x = inception_module(x, [256, 160, 320, 32, 128, 128])
x = layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)

x = inception_module(x, [256, 160, 320, 32, 128, 128])
x = inception_module(x, [384, 192, 384, 48, 128, 128])

# Average Pooling
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.4)(x)
output = layers.Dense(len(np.unique(labels)), activation='softmax')(x)

# Membuat model
model = Model(input_img, output)

# Compile model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Training Model
history = model.fit(train_datagen.flow(X_train, y_train, batch_size=32), epochs=10, validation_data=(X_test, y_test))

# Evaluasi (Akurasi, Presisi, dan Recall)
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)
y_test_classes = np.argmax(y_test, axis=1)

# Menampilkan hasil evaluasi
print(classification_report(y_test_classes, y_pred_classes, target_names=label_encoder.classes_))

# Fungsi untuk memuat dan memproses gambar dengan menampilkan satu contoh dari setiap emosi setelah CLAHE
def load_and_preprocess_images(image_dir):
    images = []
    labels = []
    example_images = {}  # Untuk menyimpan satu contoh gambar dari setiap kelas

    for label in os.listdir(image_dir):
        label_dir = os.path.join(image_dir, label)
        if os.path.isdir(label_dir):
            for img_file in os.listdir(label_dir):
                img_path = os.path.join(label_dir, img_file)
                image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Membaca gambar dalam mode grayscale
                enhanced_image = apply_clahe(image)
                resized_image = cv2.resize(enhanced_image, (128, 128))  # Resize image sesuai kebutuhan
                images.append(resized_image)
                labels.append(label)

                # Simpan satu contoh gambar dari setiap kelas emosi
                if label not in example_images:
                    example_images[label] = enhanced_image
                # Jika sudah memiliki satu contoh dari setiap kelas, lanjutkan
                if len(example_images) == len(os.listdir(image_dir)):
                    break

    # Menampilkan contoh gambar yang telah di-preprocess untuk setiap kelas
    plt.figure(figsize=(15, 10))
    for i, (emotion, img) in enumerate(example_images.items()):
        plt.subplot(2, 4, i + 1)
        plt.imshow(img, cmap='gray')
        plt.title(emotion.capitalize())
        plt.axis('off')
    plt.suptitle("Preprocessed Images After CLAHE (One from Each Emotion)")
    plt.show()

    images = np.array(images)
    images = np.expand_dims(images, axis=-1)
    labels = np.array(labels)
    return images, labels

# Load dan preprocess gambar
images, labels = load_and_preprocess_images(image_dir)

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

# Prediksi label untuk data uji
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)  # Mendapatkan indeks kelas prediksi
y_test_classes = np.argmax(y_test, axis=1)  # Mendapatkan indeks kelas sebenarnya

# Menampilkan beberapa contoh hasil prediksi
def display_classification_results(X_test, y_test_classes, y_pred_classes, label_encoder):
    plt.figure(figsize=(15, 10))
    for i in range(6):  # Menampilkan 6 contoh gambar prediksi
        plt.subplot(2, 3, i + 1)
        plt.imshow(X_test[i].reshape(128, 128), cmap='gray')
        true_label = label_encoder.inverse_transform([y_test_classes[i]])[0]
        pred_label = label_encoder.inverse_transform([y_pred_classes[i]])[0]
        plt.title(f"True: {true_label}\nPredicted: {pred_label}")
        plt.axis('off')
    plt.suptitle("Sample Predictions")
    plt.show()

# Menampilkan beberapa contoh hasil prediksi
display_classification_results(X_test, y_test_classes, y_pred_classes, label_encoder)

# Menampilkan laporan klasifikasi dengan zero_division=0 untuk mengatasi UndefinedMetricWarning
print("Classification Report:")
print(classification_report(y_test_classes, y_pred_classes, target_names=label_encoder.classes_, zero_division=0))

# Menampilkan matriks kebingungan (confusion matrix)
conf_matrix = confusion_matrix(y_test_classes, y_pred_classes)
plt.figure(figsize=(10, 8))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title("Confusion Matrix")
plt.show()

import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Fungsi untuk memuat satu contoh gambar dari setiap emosi untuk augmentasi
def load_example_images(image_dir):
    example_images = {}  # Untuk menyimpan satu contoh gambar dari setiap kelas

    for label in os.listdir(image_dir):
        label_dir = os.path.join(image_dir, label)
        if os.path.isdir(label_dir):
            for img_file in os.listdir(label_dir):
                img_path = os.path.join(label_dir, img_file)
                image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Membaca gambar dalam mode grayscale
                enhanced_image = apply_clahe(image)
                resized_image = cv2.resize(enhanced_image, (128, 128))  # Resize image sesuai kebutuhan

                # Simpan satu contoh gambar dari setiap kelas emosi
                if label not in example_images:
                    example_images[label] = np.expand_dims(resized_image, axis=-1)  # Tambahkan dimensi channel

                # Jika sudah memiliki satu contoh dari setiap kelas, lanjutkan
                if len(example_images) == len(os.listdir(image_dir)):
                    break
    return example_images

# Fungsi untuk menampilkan hasil augmentasi dari satu contoh gambar per kategori
def display_augmented_images(example_images):
    # Augmentasi (Zoom, Rotation, Flip Horizontal, dan Shear)
    datagen = ImageDataGenerator(
        zoom_range=0.2,
        rotation_range=20,
        horizontal_flip=True,
        shear_range=0.2
    )

    # Menampilkan hasil augmentasi dari satu contoh gambar per kategori
    plt.figure(figsize=(15, 15))
    for i, (emotion, img) in enumerate(example_images.items()):
        img = np.expand_dims(img, axis=0)  # Ubah gambar ke bentuk 4D untuk ImageDataGenerator
        plt.subplot(len(example_images), 6, i * 6 + 1)
        plt.imshow(img[0, :, :, 0], cmap='gray')
        plt.title(f"Original ({emotion})")
        plt.axis('off')

        # Generate dan tampilkan 5 gambar augmentasi
        for j, augmented_image in enumerate(datagen.flow(img, batch_size=1)):
            if j >= 5:  # Menampilkan 5 gambar augmentasi per kategori
                break
            plt.subplot(len(example_images), 6, i * 6 + j + 2)
            plt.imshow(augmented_image[0, :, :, 0], cmap='gray')
            plt.axis('off')
    plt.suptitle("Augmented Images (One Example from Each Emotion)")
    plt.show()

# Load satu contoh gambar dari setiap emosi
example_images = load_example_images(image_dir)

# Tampilkan hasil augmentasi
display_augmented_images(example_images)