from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('メールアドレス', 
        validators=[
            DataRequired(message='メールアドレスを入力してください'),
            Email(message='正しいメールアドレスを入力してください')
        ])
    password = PasswordField('パスワード',
        validators=[
            DataRequired(message='パスワードを入力してください'),
            Length(min=6, message='パスワードは6文字以上で入力してください')
        ])
    submit = SubmitField('ログイン')

class RegistrationForm(FlaskForm):
    username = StringField('ユーザー名',
        validators=[
            DataRequired(message='ユーザー名を入力してください'),
            Length(min=2, max=20, message='ユーザー名は2〜20文字で入力してください')
        ])
    email = StringField('メールアドレス',
        validators=[
            DataRequired(message='メールアドレスを入力してください'),
            Email(message='正しいメールアドレスを入力してください')
        ])
    password = PasswordField('パスワード',
        validators=[
            DataRequired(message='パスワードを入力してください'),
            Length(min=6, message='パスワードは6文字以上で入力してください')
        ])
    submit = SubmitField('登録') 