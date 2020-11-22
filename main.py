import re

whitespace_pattern = re.compile(r'\s')
numbers_pattern = re.compile(r'[0-9]')
letters_pattern = re.compile(r'[a-z]')


def tokenizer(_input):
    # A `current` variable for tracking our position in the code like a cursor.
    current = 0

    # And a `tokens` array for pushing our tokens too.
    tokens = []

    # We start by creating a `while` loop where we are setting up our `current`
    # variable to be incremented as much as we want `inside` the loop.
    #
    # We do this because we may want to increment `current` many times within a
    # single loop because our tokens can be any length.
    while current < len(_input):

        # store current character
        char = _input[current]

        # The first thing we want to check for is an open parenthesis. This will
        # later be used for `CallExpression` but for now we only care about the
        # character.
        #
        # We check to see if we have an open parenthesis:
        if char == '(':
            tokens.append({'type': 'paren', 'value': '('})
            current += 1
            continue

        # Next we're going to check for a closing parenthesis. We do the same exact
        # thing as before: Check for a closing parenthesis, add a new token,
        # increment `current`, and `continue`.
        if char == ')':
            tokens.append({'type': 'paren', 'value': ')'})
            current += 1
            continue

        # Moving on, we're now going to check for whitespace. This is interesting
        # because we care that whitespace exists to separate characters, but it
        # isn't actually important for us to store as a token. We would only throw
        # it out later.
        #
        # So here we're just going to test for existence and if it does exist we're
        # going to just `continue` on.
        if whitespace_pattern.match(char):
            current += 1
            continue

        # The next type of token is a number. This is different than what we have
        # seen before because a number could be any number of characters and we
        # want to capture the entire sequence of characters as one token.
        #
        #    (add 123 456)
        #         ^^^ ^^^
        # Only two separate tokens
        #
        # So we start this off when we encounter the first number in a sequence.
        if numbers_pattern.match(char):

            # We're going to create a `value` string that we are going to push characters to.
            value = ''

            # Then we're going to loop through each character in the sequence until
            # we encounter a character that is not a number, pushing each character
            # that is a number to our `value` and incrementing `current` as we go.
            while numbers_pattern.match(char):
                value += char
                current += 1
                char = _input[current]

            # After that we push our `number` token to the `tokens` array.
            tokens.append({'type': 'number', 'value': value})

            # we continue...
            continue

        # We'll also add support for strings in our language which will be any
        # text surrounded by double quotes (").
        #
        #    (concat "foo" "bar")
        #             ^^^   ^^^ string tokens
        #
        # We'll start by checking for the opening quote:
        if char == '"':

            # Keep a `value` variable for building up our string token.
            value = ''

            # We'll skip the opening double quote in our token.
            current += 1
            char = _input[current]

            # Then we'll iterate through each character until we reach another
            # double quote.
            while char != '"':
                value += char
                current += 1
                char = _input[current]

            # Skip the closing double quote.
            current += 1
            char = _input[current]

            # add `string` token to `tokens` array.
            tokens.append({'type': 'string', 'value': value})

            continue

        # The last type of token will be a `name` token. This is a sequence of
        # letters instead of numbers, that are the names of functions in our lisp
        # syntax.
        #
        #    (add 2 4)
        #     ^^^
        # Name token
        #
        if letters_pattern.match(char):
            value = ''

            # Again we're just going to loop through all the letters pushing them to `value`
            while letters_pattern.match(char):
                value += char
                current += 1
                char = _input[current]

            # and pushing that value as a token with the type `name` and continuing
            tokens.append({'type': 'name', 'value': value})
            continue

        # finally if we have not matched a character by now we are going to throw
        # an error and completely exit.
        raise TypeError('I do not know what character this is: ' + char)

    # then at the end of our `tokenizer` we simply return the `tokens` array
    return tokens


def parser(tokens):
    # `current` variable to be used as a cursor
    current = 0

    # But this time we're going to use recursion instead of a `while` loop. So we
    # define a `walk` function.
    def walk():
        nonlocal current

        # inside the walk function we start by grabbing the `current` token.
        token = tokens[current]

        # we are going to split each type of token off into different code path,
        # starting off with `number` tokens
        #
        # we test to see if we have a `number` token.
        if token['type'] == 'number':
            # if we have one, we'll increment `current`
            current += 1

            # and we'll return a new AST node called `NumberLiteral` and setting its
            #  value to the value of our token
            return {'type': 'NumberLiteral', 'value': token['value']}

        # if we have a string we will do the same as number and
        # create a `StringLiteral` node
        if token['type'] == 'string':
            current += 1

            return {'type': 'StringLiteral', 'value': token['value']}

        # Next we are going to look for CallExpressions. We start this off when
        # we encounter an open parenthesis.
        if token['type'] == 'paren' and token['value'] == '(':
            # We'll increment `current` to skip the parenthesis since we don't care
            # about it in our AST.
            current += 1
            token = tokens[current]

            # We create a base node with the type `CallExpression`, and we're going
            # to set the name as the current token's value since the next token after
            # the open parenthesis is the name of the function.
            node = {'type': 'CallExpression', 'name': token['value'], 'params': []}

            # we increment `current` again
            current += 1
            token = tokens[current]

            # And now we want to loop through each token that will be the `params` of
            # our `CallExpression` until we encounter a closing parenthesis.
            #
            # Now this is where recursion comes in. Instead of trying to parse a
            # potentially infinitely nested set of nodes we're going to rely on
            # recursion to resolve things.
            #
            # To explain this, let's take our Lisp code. You can see that the
            # parameters of the `add` are a number and a nested `CallExpression` that
            # includes its own numbers.
            #
            #   (add 2 (subtract 4 2))
            #
            # You'll also notice that in our tokens array we have multiple closing
            # parenthesis.
            #
            #   [
            #     { type: 'paren',  value: '('        },
            #     { type: 'name',   value: 'add'      },
            #     { type: 'number', value: '2'        },
            #     { type: 'paren',  value: '('        },
            #     { type: 'name',   value: 'subtract' },
            #     { type: 'number', value: '4'        },
            #     { type: 'number', value: '2'        },
            #     { type: 'paren',  value: ')'        }, <<< Closing parenthesis
            #     { type: 'paren',  value: ')'        }, <<< Closing parenthesis
            #   ]
            #
            # We're going to rely on the nested `walk` function to increment our
            # `current` variable past any nested `CallExpression`.
            #
            # So we create a `while` loop that will continue until it encounters a
            # token with a `type` of `'paren'` and a `value` of a closing
            # parenthesis.
            while token['type'] != 'paren' or (token['type'] == 'paren' and token['value'] != ')'):
                # we'll call the `walk` function which will return a `node` and we'll
                # append it into our `node.params`
                node['params'].append(walk())
                token = tokens[current]

            # finally we will increment `current` one last time to skip the closing parenthesis
            current += 1

            # And return the node
            return node

        # Again, if ww have not recognized the token type by now we are going to throw an error.
        raise TypeError(token['type'])

    # Now, we are going to create our AST which will have a root which is `Program` node
    ast = {'type': 'Program', 'body': []}

    # And we're going to kickstart our `walk` function, pushing nodes to our
    # `ast.body` array.
    #
    # The reason we are doing this inside a loop is because our program can have
    # `CallExpression` after one another instead of being nested.
    #
    #   (add 2 2)
    #   (subtract 4 2)
    #
    while current < len(tokens):
        ast['body'].append(walk())

    # At the end of our parser we'll return the AST
    return ast


def traverser(ast, visitor):
    # A `traverseArray` function that will allow us to iterate over an array and
    # call the next function that we will define: `traverseNode`.
    def traverse_array(array, parent):
        for child in array:
            traverse_node(child, parent)

    # `traverseNode` will accept a `node` and its `parent` node. So that it can
    # pass both to our visitor methods
    def traverse_node(node, parent):
        # we start by testing for the existence of a method on the visitor
        # with a matching `type`
        methods = visitor.get(node['type'])

        # If there is an `enter` method for this node type we'll call it with the
        # `node` and its `parent`.
        if methods and methods['enter']:
            methods['enter'](node, parent)

        # Next we are going to split things up by the current node type
        if node['type'] == 'Program':
            traverse_array(node['body'], node)

        # Next we do the same with `CallExpression` and traverse their `params`.
        elif node['type'] == 'CallExpression':
            traverse_array(node['params'], node)

        # In the cases of `NumberLiteral` and `StringLiteral` we don't have any
        # child nodes to visit, so we'll just break.
        elif node['type'] == 'NumberLiteral' or node['type'] == 'StringLiteral':
            pass

        # And again, if we have not recognized the node type then we will throw an error
        else:
            raise TypeError(node['type'])

        # If there is an `exit` method for this node type we will call it
        # with the `node` and its `parent`
        if methods and methods.get('exit'):
            methods['exit'](node, parent)

    # Finally we kickstart the traverser by calling th `traverse_node` with our ast
    # with no `parent` because the top level of the AST does not have a parent
    traverse_node(ast, None)


def transformer(ast):
    # We'll create a `newAst` which like our previous AST will have a program
    # node.
    new_ast = {'type': 'Program', 'body': []}

    # Next I'm going to cheat a little and create a bit of a hack. We're going to
    # use a property named `context` on our parent nodes that we're going to push
    # nodes to their parent's `context`. Normally you would have a better
    # abstraction than this, but for our purposes this keeps things simple.
    #
    # Just take note that the context is a reference *from* the old ast *to* the
    # new ast.
    ast['_context'] = new_ast['body']

    # we'll start by calling the traverser function with our ast and a visitor
    traverser(ast,
              {'NumberLiteral': {
                  'enter': lambda node, parent: parent['_context'].append(
                      {'type': 'NumberLiteral', 'value': node['value']}),
              },
                  'StringLiteral': {
                      'enter': lambda node, parent: parent['_context'].append(
                          {'type': 'StringLiteral', 'value': node['value']})
                  },
                  'CallExpression': {
                      'enter': enter_call_expression
                  }

              })

    # At the end of our transformer function we will return the
    # new ast that we just created.
    return new_ast


def enter_call_expression(node, parent):
    # We start creating a new node `CallExpression` with a nested
    # `Identifier`.
    expression = {
        'type': 'CallExpression',
        'callee': {
            'type': 'Identifier',
            'name': node['name'],
        },
        'arguments': []
    }

    #  Next we're going to define a new context on the original
    # `CallExpression` node that will reference the `expression`'s arguments
    # so that we can push arguments.
    node['_context'] = expression['arguments']

    # Then we're going to check if the parent node is a `CallExpression`.
    # If it is not...
    if parent['type'] != 'CallExpression':
        # We're going to wrap our `CallExpression` node with an
        # `ExpressionStatement`.
        expression = {
            'type': 'ExpressionStatement',
            'expression': expression
        }

    # Last, we push our (possibly wrapped) `CallExpression` to the `parent` 's
    # `context`
    parent['_context'].append(expression)


def code_generator(node):
    # we will break things down by the `type` of the `node`

    # If we have a `Program` node. We will map through each node in the `body`
    # and run them through the code generator and join them with a newline.
    if node['type'] == 'Program':
        return '\n'.join(map(code_generator, node['body']))

    # For `ExpressionStatement` we'll call the code generator on the nested
    # expression and we'll add a semicolon...
    elif node['type'] == 'ExpressionStatement':
        return code_generator(node['expression']) + ';'

    # For `CallExpression` we will print the `callee`, add an open
    # parenthesis, we'll map through each node in the `arguments` array and run
    # them through the code generator, joining them with a comma, and then
    # we'll add a closing parenthesis.
    elif node['type'] == 'CallExpression':
        return code_generator(node['callee']) + '(' + ', '.join(map(code_generator, node['arguments'])) + ')'

    # For `Identifier` we'll just return the `node`'s name.
    elif node['type'] == 'Identifier':
        return node['name']

    # For `NumberLiteral` we'll just return the `node`'s value.
    elif node['type'] == 'NumberLiteral':
        return node['value']

    # For `StringLiteral` we'll add quotations around the `node`'s value.
    elif node['type'] == 'StringLiteral':
        return '"' + node['value'] + '"'

    # And if we haven't recognized the node, we'll throw an error.
    else:
        raise TypeError(node['type'])


def compiler(input):
    tokens = tokenizer(input)
    ast = parser(tokens)
    new_ast = transformer(ast)
    output = code_generator(new_ast)

    # and simply return the output!
    return output
