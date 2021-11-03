from flask import Flask,request,jsonify
import pickle
import csv
import pandas as pd
import sklearn


##prediction = pickle.load(open('random_forest_regressor_model_prediction.pkl','rb'))
random_forest = pickle.load(open('random_forest_regressor_model.pkl','rb'))


def solve(filenames, pickle_model, path=""):
    data_dict = {"DCOILBRENTEU_CH1": "Change from year ago dollars per barrel",
                 "DCOILBRENTEU_CHG": "Change dollars per barrel",
                 "DCOILBRENTEU_PCA": "Compound annual rate of change",
                 "DCOILBRENTEU_CCA": "Continuously Compounded annual rate of change",
                 "DCOILBRENTEU_CCH": "Continuously Coumpounded rate of change",
                 "DCOILBRENTEU": "Dollars per barrel",
                 "DCOILBRENTEU_NBD19870520": "Index",
                 "DCOILBRENTEU_PC1": "percent Change from a year ago",
                 "DCOILBRENTEU_PCH": "percent change"}
    dfs = []
    for filename in filenames:
        dfs.append(pd.read_csv(filename))

    big_frame = dfs[0]
    big_frame.set_index(pd.to_datetime(big_frame['DATE']), inplace=True)

    for i in dfs:
        i.set_index(pd.to_datetime(i['DATE']), inplace=True)
        i.drop('DATE', axis=1, inplace=True)

    del (dfs[0])
    # Concatenate all data into one DataFrame
    for i in dfs:
        big_frame = pd.concat([big_frame, i], axis=1)
    big_frame.reset_index(level=['DATE'], inplace=True)
    big_frame.rename(columns=data_dict, inplace=True)

    crude_oil = big_frame
    crude_oil['yy'] = crude_oil.DATE.dt.year
    crude_oil['mm'] = crude_oil.DATE.dt.month
    crude_oil['dd'] = crude_oil.DATE.dt.day
    crude_oil['Dayofweek'] = crude_oil.DATE.dt.dayofweek
    crude_oil['Dayofyear'] = crude_oil.DATE.dt.dayofyear
    crude_oil.drop(columns='DATE', inplace=True)

    # change objects to categorical data
    df = crude_oil
    for val, cont in df.items():
        if pd.api.types.is_object_dtype(cont):
            df[val] = cont.astype("category").cat.as_ordered()

    crude_oil = df
    # Turn categorical values into numbers
    for lb, cont in crude_oil.items():
        if pd.api.types.is_categorical_dtype(cont):
            crude_oil[lb + "_is_missing"] = pd.isnull(cont)
            crude_oil[lb] = pd.Categorical(cont).codes + 1

    model = pickle.load(open(pickle_model, 'rb'))
    output = model.predict(crude_oil.drop(columns='Dollars per barrel'))
    return output

app = Flask(__name__)

@app.route('/')
def home():
    return "Bye world . Ashish mera beta hai "

@app.route('/ansDe',methods = ['POST'])
def ansDe():
    date = request.form.get('DATE')
    CH1 = request.form.get('DCOILBRENTEU_CH1')
    CHG = request.form.get('DCOILBRENTEU_CHG')
    PCA = request.form.get('DCOILBRENTEU_PCA')
    CCA = request.form.get('DCOILBRENTEU_CCA')
    CCH = request.form.get('DCOILBRENTEU_CCH')
    TEU = request.form.get('DCOILBRENTEU')
    NBD = request.form.get('DCOILBRENTEU_NBD19870520')
    PC1 = request.form.get('DCOILBRENTEU_PC1')
    PCH = request.form.get('DCOILBRENTEU_PCH')


    ##creating csv file
    filename = "user_input.csv"
    fields = ['DATE', 'DCOILBRENTEU_CH1', 'DCOILBRENTEU_CHG', 'DCOILBRENTEU_PCA','DCOILBRENTEU_CCA','DCOILBRENTEU_CCH','DCOILBRENTEU','DCOILBRENTEU_NBD19870520','DCOILBRENTEU_PC1','DCOILBRENTEU_PCH']
    rows = [[date, CH1, CHG, PCA,CCA,CCH,TEU,NBD,PC1,PCH]]
    with open(filename, 'w',encoding='UTF8', newline='') as csvfile:

        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)

    result = solve(filename,random_forest)[0]
    return jsonify({'rate':result})

if __name__ == '__main__':
    app.run(debug=True)