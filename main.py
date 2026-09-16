from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from db_config import session, engine
from sqlalchemy.orm import Session
import db_models

app = FastAPI()

# fix CORS Error, if UI is integrated
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)

# create table in db
db_models.Base.metadata.create_all(bind=engine)

@app.get("/")
def homepage():
    return "Welcome to Products app."

# dummy data
products = [
    Product(id=1, name="Phone", description="A budget phone", price=99, quantity=10),
    Product(id=2, name="Laptop", description="A gaming laptop", price=999, quantity=20),
    Product(id=3, name="Pen", description="A fountain pen", price=3, quantity=40),
    Product(id=4, name="Table", description="A computer table", price=99, quantity=10),
]

# establish the db connection, wait for its consumption to complete, then close the resource.
def manage_db_connection():
    db = session() # creating db connection
    try:
        yield db # waiting for the others to use it
    finally:
        db.close() # close the connection


# initialize table with dummy data
def init_db():
    db = session()
    # check if the table is empty -> select count(*) from table_name
    count = db.query(db_models.Product).count()

    if count == 0:
        for product in products:
            db.add(db_models.Product(**product.model_dump()))
        db.commit()
    
    db.close()
    
init_db()


@app.get("/products")
def get_all_products(db: Session = Depends(manage_db_connection)): # dependancy injection
    # query
    db_products = db.query(db_models.Product).all()
    return db_products


@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(manage_db_connection)):
    db_product = db.query(db_models.Product).filter(db_models.Product.id == id).first()
    
    if db_product:
        return db_product
    return (f"Product with id={id} not found.")


@app.post("/products")
def create_product(product: Product, db: Session = Depends(manage_db_connection)):
    product_exists = db.query(db_models.Product).filter(db_models.Product.id == product.id).first()

    if product_exists:
        return f"Product with id:{product.id} already exists, use a new id."
    else:
        db.add(db_models.Product(**product.model_dump()))
        db.commit()
        return product

@app.put("/products/{id}")
def update_product_by_id(id: int, product: Product, db: Session = Depends(manage_db_connection)):
    db_product = db.query(db_models.Product).filter(db_models.Product.id == id).first()
    
    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return "Product updated"
    else:    
        return (f"Product with id={id} not found.")

@app.delete("/products/{id}")
def delete_product_by_id(id: int, db: Session = Depends(manage_db_connection)):
    db_product = db.query(db_models.Product).filter(db_models.Product.id == id).first()

    if db_product:
        db.delete(db_product)
        db.commit()
        return "Product deleted."
    else:
        return (f"Product with id={id} not found.")    