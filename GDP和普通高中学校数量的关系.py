
# coding: utf-8

# In[74]:


import pandas as pd 


# In[75]:


import glob
print(glob.glob("*.csv"))


# In[76]:


df    = pd.read_table("GDP 666.csv",   
                       encoding = 'utf8',       
                       header = 3,              
                       skiprows = [35,36],      
                       sep =','                
                     )
df


# In[77]:


df_high_school= pd.read_table("high_school.csv",   
                       encoding = 'utf8',
                       sep =',' )


# In[78]:


df_high_school


# In[79]:


df = df_GDP
df.columns = [ int(x.replace('年','')) if x!='地区' else x for x in df.columns]
years = [ x for x in df.columns if x!='地区'] 
df_melted = pd.melt(df, id_vars=['地区'], value_vars=years)
df_melted.columns = ['地区', '年', 'GDP']
df_GDP_done = df_melted
df_GDP_done


# In[80]:


# 再处理 df_high_school
df = df_high_school
df.columns = [ int(x.replace('年','')) if x!='地区' else x for x in df.columns]
years = [ x for x in df.columns if x!='地区'] 
df_melted = pd.melt(df, id_vars=['地区'], value_vars=years)
df_melted.columns = ['地区', '年', '普通高中学校数量']
df_high_school_done = df_melted
df_high_school_done


# In[81]:


df_p = df_high_school_done.join(df_GDP_done,lsuffix='', rsuffix='_GDP')
df_p


# In[82]:


df_p.drop(["地区_GDP","年_GDP"], axis=1)


# In[84]:


df_pp = df_p.drop(["地区_GDP","年_GDP"], axis=1).set_index(["地区","年"])


# In[85]:


df_pp.query("年==2015")


# In[86]:


get_ipython().magic('matplotlib inline')
df_pp.query("年==2015").plot(kind='scatter', x='普通高中学校数量', y='GDP', 
          title = '普通高中学校数量与GDP的关系：分省数据')


# In[87]:


# 解决中文乱码问题
import matplotlib as mpl
import matplotlib.pyplot as plt
import pylab
mpl.rcParams['font.sans-serif']=['SimHei']
mpl.rcParams['axes.unicode_minus']=False

df_plot = df_pp.query("年==2015")
df_plot.plot(kind='scatter', x='普通高中学校数量', y='GDP', 
          title = '普通高中学校数量与GDP的关系：分省数据')


# In[88]:


# Regression Using Pandas and Statsmodels
import numpy as np
fit = np.polyfit(x=df_pp.query("年==2015")['普通高中学校数量'], y=df_pp.query("年==2015")['GDP'], deg=1)


# In[91]:


x=df_plot['普通高中学校数量']
y=df_plot['GDP']
ax = df_plot.plot(kind='scatter', x='普通高中学校数量', y='GDP', 
          title = '普通高中学校数量与GDP的关系：分省数据')
ax.plot(x, fit[0] * x + fit[1], color='yellow')
ax.scatter(x, y)


# In[92]:


df_pp 


# In[93]:


# tooltip 工具提示 
df_pp['desc'] = df_pp.index.get_level_values(0)


# In[96]:


# 制图
from bokeh.plotting import figure, output_file, show, output_notebook
from bokeh.models import HoverTool, BoxSelectTool

title = '分省数据' 
xlabel = '普通高中学校数量：个数' 
ylabel = 'GDP：产值'

hover = HoverTool(
    tooltips=[
        ( '个数',  '$x{0,F}'), 
        ( '产值',  '$y{0,F}'),
        ( '地区',  '@desc'  ),
    ]
)

TOOLS = [hover, "pan, wheel_zoom, box_zoom, reset, resize"]
fig = figure(plot_width=800, plot_height=600,
           x_axis_label = xlabel, y_axis_label = ylabel, 
           title=title, tools=TOOLS)

df_plot = df_pp.query("年==2015")

fig.circle("普通高中学校数量", "GDP",
         source = df_plot,
         fill_alpha=0.6, line_color=None, size= 30)

#regression line
xs = [min(df_plot["普通高中学校数量"]), max(df_plot["普通高中学校数量"])]
fig.line(x=xs, y=[ fit[0] * x + fit[1] for x in xs] )

output_notebook() # 输出到IPython/Jupyter Notebook，若要输出到他处需调整
#output_file('by_provinces.htm') # 输出到 htm
show(fig)


# In[97]:


from bokeh.plotting import figure
from bokeh.io import output_notebook, push_notebook, show
from bokeh.models import CustomJS, Slider,HoverTool, BoxSelectTool
from bokeh.layouts import column

title = '分省数据' 
xlabel = '普通高中学校数量：个数' 
ylabel = 'GDP：产值大小'
hover = HoverTool(
    tooltips=[
        ( '个数大小',  '$x{0,F}'), 
        ( '产值大小',  '$y{0,F}'),
        ( '地区',  '@desc'  ),
    ]
)

TOOLS = [hover, "pan, wheel_zoom, box_zoom, reset, resize"]

fig = figure(plot_width=800, plot_height=600,
           x_axis_label = xlabel, y_axis_label = ylabel, 
           title=title, tools=TOOLS)

yr_min = df_pp.index.get_level_values(1).min()
df_plot = df_pp.query("年=={yr}".format(yr=yr_min))
plt = fig.circle("普通高中学校数量", "GDP",
         source = df_plot,
         fill_alpha=0.6, line_color=None, size= 15)


def update_plot(year):
    #plt.data_source.data = df_pp.query("年=={yr}".format(yr=year))
    plt.data_source.data['普通高中学校数量'] = list(df_pp.query("年=={yr}".format(yr=year)).loc[:,['普通高中学校数量']].iloc[:,0].values)
    plt.data_source.data['GDP'] = list(df_pp.query("年=={yr}".format(yr=year)).loc[:,['GDP']].iloc[:,0].values)
    plt.data_source.data['地区_年'] = [(x[0],int(year)) for x in plt.data_source.data['地区_年']]

    push_notebook(handle=bokeh_handle)  
    print (year)
    ##### new notebook cell #####

callback = CustomJS(code="""
if (IPython.notebook.kernel !== undefined) {
    var kernel = IPython.notebook.kernel;
    cmd = "update_plot(" + cb_obj.value + ")";
    kernel.execute(cmd, {}, {});
}
""")

slider = Slider(start=df_pp.index.get_level_values(1).min(), 
                end=df_pp.index.get_level_values(1).max(),
                value=1,
                step=1,
                title="年",
                callback=callback)
output_notebook()

bokeh_handle = show(column(slider, fig), notebook_handle=True)

