from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
import os
import math
import pandas as pd
import sys
from matplotlib.offsetbox import AnchoredText
import matplotlib
matplotlib.use('Agg')

def RP():
    def sort_key(item):
        split_item = item.rsplit('.', 1)[0].split("_")
        cycle_index = Cycled.index(split_item[2])
        position_index = Position.index(split_item[1])
        upper_index = Upper.index(split_item[3])
        no_index = NO.index(int(split_item[5]))
        balde_index = blade.index(split_item[4])
        return cycle_index,balde_index, position_index, no_index,upper_index

    def imag_20(img_files,img_files2,df):
        
        img_files = img_files[:32]
        img_files2 = img_files2[:32]
        fig = plt.figure(
            figsize=(30,50)
        )

        rows = math.ceil(len(img_files) / 4)

        for i, (img_file, img_file2) in enumerate(zip(img_files, img_files2)):
            ax = fig.add_subplot(rows, 4, i+1)
            img = Image.open(os.path.join(img_dir, img_file))
            ax.imshow(img, aspect=1)
            ax.axis('off')
            a= df.loc[df['new'] == img_file2, 'WQ actual'].tolist()
            b= df.loc[df['new'] == img_file2, 'New blade'].tolist()
            Side12 = img_file2.split('_')[0]
            Cycles12 = img_file2.split('_')[1]
            Position12 = img_file2.split('_')[2]
            title =ax.set_title(f'Side: {Side12}\nPosition: {Position12}\nWQ score: {int(a[0])}', fontsize=25)
            if b[0]== "old":#Old blade        
                if a[0] >old:
                    title.set_bbox(dict(facecolor='lightgreen', alpha=0.5, edgecolor='lightgreen'))        
                if a[0] <=old:
                    title.set_bbox(dict(facecolor='red', alpha=0.5, edgecolor='red'))
                if i%4 ==0:
                    fig.text(0.5, 0.99-(i/(rows)/4), f'After {Cycles12} Cycles', ha='center', va='center', fontsize=30, fontweight='bold')
            if b[0]== "new":#New blade  
                if a[0] >new:
                    title.set_bbox(dict(facecolor='lightgreen', alpha=0.5, edgecolor='lightgreen'))        
                if a[0] <=new:
                    title.set_bbox(dict(facecolor='red', alpha=0.5, edgecolor='red'))
                if i%4 ==0:
                    fig.text(0.5, 0.99-(i/(rows)/4), f'\nAfter {Cycles12} Cycles\nNew Blade', ha='center', va='center', fontsize=30, fontweight='bold')
        plt.suptitle(f"{plat}", fontsize=40, y=1.0, x=0.2)
        fig.subplots_adjust(wspace=0.1, hspace=0.2)
        plt.tight_layout()
        #plt.show()
        return fig

    def left(img_files,df):
        img_files = [f for f in os.listdir(img_dir) if f.endswith('.JPG')]
        img_files.sort(key=sort_key)
        df = df[df["Mistake"]==False]
        df = df[df["Test ID"]==ID1]
        df['Direction'] = df['Direction'].replace({'PP': 'DOWN', 'URP': 'UP'})
        df['Side'] = df['Side'].replace({'Left': 'PS', 'Right': 'DS'})
        df = df[df["WQ sec"]==3]
        df['new'] = df["Side"]+'_'+df["Cycle"] + '_' + df["Direction"] + '_'+ df["New blade"]
        img_files = [item for item in img_files if "_3.JPG" in item]
        img_files2 = [f.split('_', 1)[1].rsplit('.', 1)[0] for f in img_files]
        img_files2 = [f.replace('Left', 'PS').replace('Right', 'DS') for f in img_files2]
        img_files2 = [f.replace('PP', 'DOWN').replace('URP', 'UP') for f in img_files2]
        img_files2 = [f.rsplit('_', 1)[0] for f in img_files2]
        if len(img_files)>20:
            my_figure = imag_20(img_files,img_files2,df)
            return my_figure 

    ID1 = "Test"
    new =8
    old =6 
    plat="Rivian"
    #ID1 = sys.argv[1]
    #new = int(sys.argv[2])
    #old = int(sys.argv[3])
    #plat = sys.argv[4]
    img_dir = f'static/Report/{ID1}/'
    img_files = []
    df = pd.read_excel('static/log.xlsx')

    Position = ["Left","Right"]
    Cycled = ["0K", "100K","200K","300K","400K","500K","600K","700K","800K","900K","1.0M","1.1M","1.2M","1.3M","1.4M","1.5M","1.6M","1.7M","1.8M","1.9M","2.0M","2.1M","2.2M","2.3M","2.4M","2.5M","2.6M","2.7M","2.8M","2.9M","3.0M",]
    Upper=["URP","PP"]
    NO = [0,3]
    blade = ["old","new"]

    my_figure = left(img_files,df)
    pp = PdfPages(f'static/Report/{ID1}/Report_after3sec_1.pdf')
    # 画像をPDFとして保存する
    pp.savefig(my_figure)
    # PDFの保存終了
    pp.close()