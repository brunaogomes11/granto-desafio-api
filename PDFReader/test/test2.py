all_text =  ['dasdsadasd- adasdasdasdasdasdas dasdasdsadsa-  asdagfdgdfgfd']

a = list(map(lambda text: text.replace('- ', '  '), all_text))

print(a)