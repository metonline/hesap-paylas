#!/usr/bin/env python
# Test Flask POST method support

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/test', methods=['POST'])
def test_post():
    return jsonify({'message': 'POST works'}), 200

@app.route('/test2', methods=['GET', 'POST'])
def test_both():
    return jsonify({'method': request.method}), 200

if __name__ == '__main__':
    with app.app_context():
        print("All registered routes:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.rule:30} Methods: {sorted(rule.methods)}")
