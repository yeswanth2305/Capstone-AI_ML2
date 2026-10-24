# Module 2 — Analytics and Predictive Modeling

## Overview

This module performs exploratory data analysis and predictive modeling on the Titanic dataset using Python, pandas, seaborn, matplotlib, and scikit-learn.

The dataset is loaded once using `seaborn.load_dataset("titanic")` in `01_eda.ipynb` and saved locally as `titanic.csv`. The modeling notebook reads this local CSV so that the modeling workflow can run without requiring another network download.

## Dataset and Cleaning

The EDA workflow reports:

* Dataset shape and structure
* Descriptive statistics
* Missing-value percentages
* Age and fare distributions
* IQR-based outlier counts
* Fare mean, median, mode, and skewness
* Survival rates by sex and passenger class
* Correlation analysis
* Multivariate visualizations

Missing values were handled according to the assignment threshold:

* Missingness below 5%: affected rows were dropped.
* Missingness from 5% to 30%: values were imputed.
* Very high missingness: the affected column was removed when reliable imputation was not appropriate.

In the Titanic dataset, `age` was median-imputed, the very small number of missing `embarked` and `embark_town` observations were handled by dropping affected rows, and `deck` was removed because approximately 77% of its values were missing.

The exploratory standardization of `age` and `fare` was performed only as a sanity check. It was not reused as the modeling preprocessing.

## Classification

The classification target is `survived`.

Features used include:

* `age`
* `fare`
* `sex`
* `embarked`
* `pclass`
* `sibsp`
* `parch`

The following models were evaluated:

1. Logistic Regression
2. Decision Tree
3. Random Forest

The workflow uses a stratified 80/20 train/test split. Preprocessing is performed inside a `ColumnTransformer` and model `Pipeline` to prevent data leakage.

Numeric variables use median imputation and standardization. Categorical variables use most-frequent imputation followed by one-hot encoding.

The models are evaluated using:

* Accuracy
* Precision
* Recall
* F1 score
* ROC-AUC
* Confusion matrices
* ROC curves

A Decision Tree visualization is also generated.

## Class Imbalance

Three Logistic Regression variants are compared:

1. Baseline Logistic Regression
2. Logistic Regression with `class_weight="balanced"`
3. Logistic Regression with SMOTE

SMOTE is applied only inside the training pipeline so that the test set remains untouched.

## Random Forest Tuning

Random Forest hyperparameters are optimized using `GridSearchCV`.

The search includes:

* `n_estimators`
* `max_depth`
* `max_features`

The tuned Random Forest also uses `oob_score=True`, and the resulting out-of-bag score is reported.

## Regression

A multivariate Linear Regression model predicts `fare` using passenger characteristics.

Regression metrics reported are:

* MAE
* RMSE
* R²
* Adjusted R²

A residual plot is generated to assess the error structure and visually evaluate potential heteroscedasticity.

## Saved Model

The final tuned Random Forest pipeline is saved as:

```text
models/titanic_pipeline.joblib
```

The saved artifact contains both preprocessing and the estimator, allowing raw input data to be passed directly to the reloaded pipeline.

## Outputs

Generated results include:

```text
outputs/
├── classification_results.csv
├── final_classification_results.csv
├── imbalance_results.csv
├── regression_results.csv
├── final_model_report.txt
├── cleaning_decisions.csv
├── eda_results.txt
└── figures/
```

## Running

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the notebooks in order:

```text
01_eda.ipynb
02_modeling.ipynb
```

`01_eda.ipynb` creates the offline `titanic.csv` dataset used by `02_modeling.ipynb`.
