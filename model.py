import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import confusion_matrix, accuracy_score
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import TensorBoard, ModelCheckpoint, ReduceLROnPlateau, EarlyStopping

# Load the dataset
dataset = pd.read_csv("data.csv")

# Splitting the dataset into features (X) and target (y)
X = dataset.iloc[:, :-1].values  # Exclude the first column (user ID)
y = dataset.iloc[:, -1].values    # Target column (mental health levels)

label_encoders = []
for col in range(X.shape[1]):
    if isinstance(X[0, col], str):
        label_encoder = LabelEncoder()
        X[:, col] = label_encoder.fit_transform(X[:, col])
        label_encoders.append(label_encoder)

# Debugging: Print unique values in each column to identify unexpected values
for col in range(X.shape[1]):
    unique_values = np.unique(X[:, col])
    print(f"Column {col}: {unique_values}")

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Initialize the ANN
model = Sequential()

# Adding the input layer and the first hidden layer
model.add(Dense(units=64, activation='relu', input_dim=X_train.shape[1]))

# Adding more hidden layers if needed
model.add(Dense(units=64, activation='relu'))

# Adding the output layer
model.add(Dense(units=len(np.unique(y)), activation='linear'))

# Compiling the ANN
optimizer=keras.optimizers.Adam(learning_rate=3e-4)
model.compile(optimizer=optimizer, loss='mse', metrics=['accuracy'])

# Training the ANN on the Training set
from datetime import datetime
t=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

tb=TensorBoard(log_dir='logs/'+t)
es=EarlyStopping(patience=50, restore_best_weights=True)
rlr=ReduceLROnPlateau(factor=0.9, patience=50,cooldown=30)
mc=ModelCheckpoint(filepath='model-{epoch:03d}-{loss:.4f}-{val_loss:.4f}.h5',save_best_only=True)

model.fit(X_train, y_train, batch_size=32, epochs=5000, validation_split=0.2, callbacks=[tb,es,rlr,mc], shuffle=True)

# Predicting the Test set results
y_pred = model.predict(X_test)
y_pred = np.argmax(y_pred, axis=1)

model.save('model.h5')