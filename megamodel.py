import lightgbm as lgb
import pandas as pd
import random
import numpy as np
import mlflow

pos_csv = r"/data/positives/out_fix.csv"
neg_csv = r"/data/negatives/out_fix.csv"
#TODO: correct the number of records here
#adjust so two skips to account for different size of neg and pos  52602
default_seq_len = 200
seq_lens = [10,20,24,30,36,40,50,60,70,86,100,126,150,200]
num_leaves = [5,20,50,200]
n_pos = 52602 #number of positive samples
n_neg = 26190 #number of records in file
s_pos = int(0.8*n_pos) #desired sample size
s_neg = int(0.8*n_neg) #desired percentage of negative samples, maybe adjust this to oversample negative samples
skip_pos = sorted(random.sample(range(n_pos),n_pos-s_pos))
skip_neg = sorted(random.sample(range(n_neg),n_neg-s_neg))
leftover_pos = sorted(set(range(n_pos)) - set(skip_pos))
leftover_neg = sorted(set(range(n_neg)) - set(skip_neg))



# %%
random.shuffle(skip_pos)
random.shuffle(skip_neg)
val_pos = leftover_pos + skip_pos[0:int(len(skip_pos)/2)]
pred_pos = leftover_pos + skip_pos[int(len(skip_pos)/2):]
val_neg = leftover_neg + skip_neg[0:int(len(skip_neg)/2)]
pred_neg = leftover_neg + skip_neg[int(len(skip_neg)/2):]
skip_pos = sorted(skip_pos)
skip_neg = sorted(skip_neg)
val_pos = sorted(val_pos)
val_neg = sorted(val_neg)
pred_pos = sorted(pred_pos)
pred_neg = sorted(pred_neg)

# %%
train_pos_csv  = pd.read_csv(pos_csv, skiprows=skip_pos, delimiter=r'\n')
train_neg_csv  = pd.read_csv(neg_csv, skiprows=skip_neg, delimiter=r'\n')
val_pos_csv  = pd.read_csv(pos_csv, skiprows=leftover_pos, delimiter=r'\n')
val_neg_csv  = pd.read_csv(neg_csv, skiprows=leftover_neg, delimiter=r'\n')
pred_pos_csv  = pd.read_csv(pos_csv, skiprows=pred_pos, delimiter=r'\n')
pred_neg_csv  = pd.read_csv(neg_csv, skiprows=pred_neg, delimiter=r'\n')


# %%
train_pos_csv['label'] = 1
train_neg_csv['label'] = 0
val_pos_csv['label'] = 1
val_neg_csv['label'] = 0
val_pos_csv .columns = ['sequence', 'label']
val_neg_csv.columns = ['sequence', 'label']
train_pos_csv .columns = ['sequence', 'label']
train_neg_csv.columns = ['sequence', 'label']
# append both df to one df
total_df = pd.concat([train_pos_csv, train_neg_csv], axis=0, ignore_index=True)
#append both validation df to one df
val_df = pd.concat([val_pos_csv, val_neg_csv], axis=0, ignore_index=True)
#shuffle data
c = total_df.sample(frac=1).reset_index(drop=True)
c_val = val_df.sample(frac=1).reset_index(drop=True)

# %%
pred_pos_csv['label']=1
pred_neg_csv['label']=0
pred_pos_csv.columns = ['sequence', 'label']
pred_neg_csv.columns = ['sequence', 'label']
pred_df = pd.concat([pred_pos_csv, pred_neg_csv], axis=0, ignore_index=True)
c_pred = pred_df.sample(frac=1).reset_index(drop=True)



# %%
c['sequence']= c['sequence'].astype(str)
c_val['sequence']= c_val['sequence'].astype(str)
c_pred['sequence']= c_pred['sequence'].astype(str)

# %%
train_df = c['sequence'].str.split(',',expand=True)
val_df = c_val['sequence'].str.split(',',expand=True)
pred_df = c_pred['sequence'].str.split(',',expand=True)

# %%
val_df.drop(val_df.columns[len(val_df.columns)-1], axis=1, inplace=True)
train_df.drop(train_df.columns[len(train_df.columns)-1], axis=1, inplace=True)
pred_df.drop(pred_df.columns[len(pred_df.columns)-1], axis=1, inplace=True)

# %%
val_df.drop(val_df.columns[0], axis=1, inplace=True)
train_df.drop(train_df.columns[0], axis=1, inplace=True)
pred_df.drop(pred_df.columns[0], axis=1, inplace=True)

train_df = train_df.replace('NA', np.nan)
train_df = train_df.replace('None', np.nan)
val_df = val_df.replace('NA', np.nan)
val_df = val_df.replace('None', np.nan)
pred_df = pred_df.replace('NA', np.nan)
pred_df = pred_df.replace('None', np.nan)

val_weight_df = val_df[201]
val_df.drop(val_df.columns[200], axis=1, inplace=True)
train_weight_df = train_df[201]
train_df.drop(train_df.columns[200], axis=1, inplace=True)
pred_weight_df = pred_df[201]
pred_df.drop(pred_df.columns[200], axis=1, inplace=True)

val_df =pd.concat([val_df, val_weight_df],ignore_index = True, axis=1)
train_df =pd.concat([train_df, train_weight_df],ignore_index = True, axis=1)
pred_df =pd.concat([pred_df, pred_weight_df],ignore_index = True, axis=1)

train_df['label'] = c['label']
val_df['label'] = c_val['label']
pred_df['label'] = c_pred['label']

# %%
cate = [i for i in range(0, default_seq_len)]
non_cate = [i for i in train_df.columns if i not in cate]
val_non_cate = [i for i in val_df.columns if i not in cate]

to_drop = []
val_drop = []
pred_drop = []
for i in non_cate:
    try:
        train_df[i] = train_df[i].astype('float32')
    except:
        to_drop.append(i)
    try:
        val_df[i] = val_df[i].astype('float32')
    except:
        val_drop.append(i)
    try:
        pred_df[i] = pred_df[i].astype('float32')
    except:
        pred_drop.append(i)


train_drop = []
val_drop = []
pred_drop = []
for col in cate:
    try:
        train_df[col] = train_df[col].astype('int32')
    except:
        train_drop.append(col)
    try:
        val_df[col] = val_df[col].astype('int32')
    except:
        val_drop.append(col)
    try:
        pred_df[col] = pred_df[col].astype('int32')
    except:
        pred_drop.append(col)
    
for seq_len in seq_lens:
    num_remove = default_seq_len - seq_len
    margin = int(num_remove/2)
    cols_rem = [i for i in range(margin)] + [i for i in range(default_seq_len-margin, default_seq_len+margin)] + [i for i in range(default_seq_len*2-margin, default_seq_len*2+margin)] + [i for i in range(default_seq_len*3-margin, default_seq_len*3+margin)] + [i for i in range(default_seq_len*4-margin, default_seq_len*4+margin)] + [i for i in range(default_seq_len*5-margin,default_seq_len*5)]
    non_target = [i for i in train_df.columns if i != 'label' and i not in cols_rem]
    target = ['label']
    categorical = [i for i in range(0, seq_len)]
    train_data = lgb.Dataset(train_df[non_target], label=train_df[target], categorical_feature=categorical, free_raw_data=False)
    validation_data = train_data.create_valid(val_df[non_target], label=val_df[target])
    for num in num_leaves:
        param = {'num_leaves': num, 'objective': 'binary', 'pos_bagging_fraction' : .45, 'neg_bagging_fraction' : .9, 'force_col_wise' : 'true'}
        param['metric'] = ['auc', 'binary_logloss']

        num_round = 500
        print(f'num_leaves: {num}, seq_len: {seq_len}')
        bst = lgb.train(param, train_data, num_round, valid_sets=validation_data, callbacks=[lgb.early_stopping(stopping_rounds=10)],)
        bst.save_model(f'model_{num}_{seq_len}.txt', num_iteration=bst.best_iteration)

 
