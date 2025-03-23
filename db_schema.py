from app import create_app
from app.extensions import db
from sqlalchemy import inspect

def print_table_schema():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # revenue_plansテーブル
        print("\n=== revenue_plans テーブル ===")
        columns = inspector.get_columns('revenue_plans')
        for column in columns:
            print(f"カラム名: {column['name']}")
            print(f"型: {column['type']}")
            print(f"NULL許可: {column.get('nullable', True)}")
            print("---")

        # revenue_plan_valuesテーブル
        print("\n=== revenue_plan_values テーブル ===")
        columns = inspector.get_columns('revenue_plan_values')
        for column in columns:
            print(f"カラム名: {column['name']}")
            print(f"型: {column['type']}")
            print(f"NULL許可: {column.get('nullable', True)}")
            print("---")

        # revenue_plan_detailsテーブル
        print("\n=== revenue_plan_details テーブル ===")
        columns = inspector.get_columns('revenue_plan_details')
        for column in columns:
            print(f"カラム名: {column['name']}")
            print(f"型: {column['type']}")
            print(f"NULL許可: {column.get('nullable', True)}")
            print("---")

        # 外部キー制約の表示
        for table_name in ['revenue_plans', 'revenue_plan_values', 'revenue_plan_details']:
            print(f"\n=== {table_name}の外部キー ===")
            for fk in inspector.get_foreign_keys(table_name):
                print(f"参照元: {fk['referred_table']}.{fk['referred_columns']}")
                print(f"参照カラム: {fk['constrained_columns']}")
                print("---")

if __name__ == '__main__':
    print_table_schema() 