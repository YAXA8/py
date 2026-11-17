import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression   #class from linear_model module
from sklearn.model_selection import train_test_split  # Function from model_selection module
from sklearn.metrics import mean_squared_error, r2_score  # Function from metrics module

# 1. Create simple sample data: y = 2.5 * x + 10 + noise
np.random.seed(42)
X = 2 * np.random.rand(100, 1)  # 100 random values between 0 and 2, 100 rows and 1 column. x needs to be 2 dimensional, cause we might have multiple x(for ex for house: size,number of beds,...)
y = 2.5 * X.squeeze() + 10 + np.random.randn(100) * 0.5  # Linear relation + Gaussian noise. but because y is one its 1 dimensional

# 2. Split into train and test sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3. Initialize and fit the Linear Regression model
model = LinearRegression() # LinearRegression alone is just the class, the parentheses actually create the model object you can fit and use, empty parentheses means use the default settings
model.fit(X_train, y_train)
print(model)