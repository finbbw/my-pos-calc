import streamlit as st
import pyperclip
@st.cache
def orginal_paperclip():
    # function logic here
    test = pyperclip.paste()
    #st.write (test)
    return (test)
    
a = orginal_paperclip()
#length_new = len(a)
st.write ('Orginal string from paperclip:')
st.write (a)


def add_to_clipboard(symbol, current_value):
    combined_value = current_value + ', ' + symbol if current_value else symbol
    pyperclip.copy(combined_value)
    return combined_value

symbols = pyperclip.paste().split(',')
number_of_symbols = len(symbols)

symbol_string = pyperclip.paste().split(',')
length = len(symbol_string)
#print(length)

current_value = pyperclip.paste()
#current_value = pyperclip.copy('')

#symbol = 'Test'

counter = 0
for symbol in symbols:
    st.write("Displaying chart for: ", symbol)
    st.image(f"https://finviz.com/chart.ashx?t={symbol}")
    button_id = symbol + "_" + str(counter)
    if st.button(f"Add {symbol} to Clipboard", key=button_id):
        current_value = add_to_clipboard(symbol, current_value)
        #st.write (current_value)
    counter += 1



#paperclip = pyperclip.paste()
#result = paperclip.split(',')[-(number_of_symbols):]
#result = ', '.join(result)

#st.write (number_of_symbols)
#st.write (result)
#st.write(current_value)
#result = current_value
#test = pyperclip.paste()
#st.write (test)
ln = len(a)
#st.write (ln)
#r = result [-ln:]

#st.write (a)
#ln = len(a)
#st. write (current_value)




def drop_first_19_characters(string):
    #return string[(19):]
    return string[ln:]

string = current_value

st.write ('Orginal string from paperclip:')
st.write (a)

st.write("Current String: ")
st.write (current_value)

if st.sidebar.button("Drop orginal paperclip stocks",key='drop'):
    newstring = drop_first_19_characters(string)
    #st.write("New String:\n ", newstring)
    if newstring[0] == ',':
        newstring = newstring[1:]
    st.write("New String:\n ", newstring)
    pyperclip.copy(newstring)    



     








