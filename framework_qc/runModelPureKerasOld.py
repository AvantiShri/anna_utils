#This is a model implemented in "pure keras" for DMSO sequence x matrix x positional values, goal is to see if recallAtFDR50 reproduces results from momma_dragonn 
import imp
import argparse
import h5py
import numpy as np 
global modelModule

def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("--train_path")
    parser.add_argument("--valid_path")
    parser.add_argument("--test_path")
    parser.add_argument("--model_output_file")
    parser.add_argument("--model_builder")
    parser.add_argument("--w0_file")
    parser.add_argument("--w1_file")
    parser.add_argument("--batch_size",type=int,default=1000)
    return parser.parse_args() 

def load_data(args):
    trainmat=h5py.File(args.train_path,'r')
    num_train=args.batch_size*(trainmat['Y']['output'].shape[0]/args.batch_size)
    validmat=h5py.File(args.valid_path,'r')
    num_valid=args.batch_size*(validmat['Y']['output'].shape[0]/args.batch_size) 
    return trainmat,validmat,num_train,num_valid 

        
def fit_and_evaluate(model,train_gen,validation_data,num_train,num_valid,args):
    model_output_path = args.model_output_file
    from keras.callbacks import TensorBoard, ModelCheckpoint, EarlyStopping,CSVLogger    
    checkpointer = ModelCheckpoint(filepath=model_output_path, verbose=1, save_best_only=True)
    earlystopper = EarlyStopping(monitor='val_loss', patience=3, verbose=1)
    csvlogger = CSVLogger(args.model_output_file+".log", append = True)
    np.random.seed(1234) 
    model.fit_generator(train_gen,
                        validation_data=validation_data,
                        samples_per_epoch=num_train,
                        nb_epoch=20,
                        verbose=1,
                        callbacks=[checkpointer,earlystopper,csvlogger])#,  tensorboard])
    print("complete!!") 
    #results = model.evaluate(x_valid,
    #                         y_valid,
    #                         batch_size=1000,
    #                         verbose=1)
    #print str(results)


def main():
    args=parse_args()
    train_mat,valid_mat,num_samples_train,num_samples_valid= load_data(args)
    modelModule=imp.load_source('name',args.model_builder)
    train_generator=modelModule.data_generator(train_mat,args)
    validation_x=np.asarray(valid_mat['X']['sequence'])
    validation_y=np.asarray(valid_mat['Y']['output'])
    validation_data={"sequence":validation_x,"output":validation_y}
    #valid_generator=modelModule.data_generator(valid_mat,args) 
    model=modelModule.create_model(args.w0_file,args.w1_file)
    fit_and_evaluate(model,train_generator,
                     validation_data,
                     num_samples_train,
                     num_samples_valid,args) 

if __name__=="__main__":
    main() 
