from main import transformer, compiler, code_generator, parser, tokenizer

test_input = '(add 2 (substract 4 2))'
output = 'add(2, substract(4, 2));'

TOKENS = [{'type': 'paren', 'value': '('}, {'type': 'name', 'value': 'add'}, {'type': 'number', 'value': '2'},
          {'type': 'paren', 'value': '('}, {'type': 'name', 'value': 'substract'}, {'type': 'number', 'value': '4'},
          {'type': 'number', 'value': '2'}, {'type': 'paren', 'value': ')'}, {'type': 'paren', 'value': ')'}]

AST = {'type': 'Program', 'body': [{'type': 'CallExpression', 'name': 'add',
                                    'params': [{'type': 'NumberLiteral', 'value': '2'},
                                               {'type': 'CallExpression', 'name': 'substract',
                                                'params': [{'type': 'NumberLiteral', 'value': '4'},
                                                           {'type': 'NumberLiteral', 'value': '2'}]}]}]}

NEW_AST = {'type': 'Program', 'body': [{'type': 'ExpressionStatement', 'expression': {'type': 'CallExpression',
                                                                                      'callee': {'type': 'Identifier',
                                                                                                 'name': 'add'},
                                                                                      'arguments': [
                                                                                          {'type': 'NumberLiteral',
                                                                                           'value': '2'},
                                                                                          {'type': 'CallExpression',
                                                                                           'callee': {
                                                                                               'type': 'Identifier',
                                                                                               'name': 'substract'},
                                                                                           'arguments': [
                                                                                               {'type': 'NumberLiteral',
                                                                                                'value': '4'},
                                                                                               {'type': 'NumberLiteral',
                                                                                                'value': '2'}]}]}}]}

assert tokenizer(test_input) == TOKENS, 'Tokenizer should turn `input` string into `tokens` array'
assert parser(TOKENS) == AST, 'Parser should turn `tokens` array into `ast`'
assert transformer(AST) == NEW_AST, 'Transformer should turn `ast` into a `newAst`'
assert code_generator(NEW_AST) == output, 'Code Generator should turn `newAst` into `output` string'
assert compiler(test_input) == output, 'Compiler should turn `input` into `output`'
