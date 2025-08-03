import os
import joblib
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.exceptions import ConvergenceWarning
import warnings

warnings.filterwarnings("ignore", category=ConvergenceWarning)

def prepare_data_for_ml(filename):
    df = pd.read_csv(filename)
    df = df.sort_values('Date').reset_index(drop=True)
    features = ['RSI', 'MACD', 'MACD_signal', 'Volume']
    df = df.dropna(subset=features)
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    return df, features

def train_and_evaluate(df, features, ticker):
    os.makedirs("saved_models", exist_ok=True)

    df = df.dropna().reset_index(drop=True)
    df_model = df.iloc[:-1].copy()  # exclude last row for prediction
    X = df_model[features]
    y = df_model['Target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # --- Decision Tree
    dt = DecisionTreeClassifier(random_state=42)
    dt.fit(X_train, y_train)
    acc_dt = accuracy_score(y_test, dt.predict(X_test))

    # --- Logistic Regression (Grid Search)
    lr = LogisticRegression(max_iter=1000, solver='liblinear')
    lr_params = {'C': [0.01, 0.1, 1, 10], 'penalty': ['l1', 'l2']}
    grid_lr = GridSearchCV(lr, lr_params, cv=3, n_jobs=-1)
    grid_lr.fit(X_train, y_train)
    best_lr = grid_lr.best_estimator_
    acc_lr = accuracy_score(y_test, best_lr.predict(X_test))
    joblib.dump(best_lr, f"saved_models/{ticker}_lr_model.joblib")

    # --- Random Forest (Grid Search)
    rf = RandomForestClassifier(random_state=42)
    rf_params = {
        'n_estimators': [50, 100],
        'max_depth': [3, 5, None],
        'min_samples_split': [2, 5]
    }
    grid_rf = GridSearchCV(rf, rf_params, cv=3, n_jobs=-1)
    grid_rf.fit(X_train, y_train)
    best_rf = grid_rf.best_estimator_
    acc_rf = accuracy_score(y_test, best_rf.predict(X_test))
    joblib.dump(best_rf, f"saved_models/{ticker}_rf_model.joblib")

    # --- Voting Classifier
    voting_clf = VotingClassifier(
        estimators=[('dt', dt), ('lr', best_lr), ('rf', best_rf)],
        voting='soft'
    )
    voting_clf.fit(X_train, y_train)
    acc_voting = accuracy_score(y_test, voting_clf.predict(X_test))
    joblib.dump(voting_clf, f"saved_models/{ticker}_voting_model.joblib")

    # --- Choose best model
    accs = {
        'DecisionTree': acc_dt,
        'LogisticRegression': acc_lr,
        'RandomForest': acc_rf,
        'Voting': acc_voting
    }
    best_model_name = max(accs, key=accs.get)
    best_model = {
        'DecisionTree': dt,
        'LogisticRegression': best_lr,
        'RandomForest': best_rf,
        'Voting': voting_clf
    }[best_model_name]

    # --- Inference on full dataset (except last row)
    df_model['ML_Prediction'] = best_model.predict(df_model[features])
    df_model['Model'] = best_model_name
    df_model['Model_Accuracy'] = round(accs[best_model_name] * 100, 2)

    # --- Inference on latest row
    latest_row = df.iloc[-1][features].values.reshape(1, -1)
    latest_pred = best_model.predict(latest_row)[0]

    latest_data = df.iloc[-1].copy()
    latest_data['ML_Prediction'] = latest_pred
    latest_data['Model'] = best_model_name
    latest_data['Model_Accuracy'] = round(accs[best_model_name] * 100, 2)

    # --- Append to df_model
    df_model = pd.concat([df_model, pd.DataFrame([latest_data])], ignore_index=True)


    print(f"[INFO] Best model for {ticker}: {best_model_name} with accuracy {accs[best_model_name]:.2f}")

    return df_model

def create_trade_log(df, ticker):
    trade_log = df[df['Signal'] != 0].copy()
    trade_log['Ticker'] = ticker
    trade_log['Reason'] = trade_log['Signal'].apply(
        lambda x: 'RSI & MA Crossover Buy' if x == 1 else 'Sell Signal'
    )
    trade_log = trade_log[[
        'Date', 'Ticker', 'Signal', 'Close', 'RSI', 'MA20', 'MA50',
        'ML_Prediction', 'Model', 'Model_Accuracy', 'Reason'
    ]]
    return trade_log

