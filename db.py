from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

Database_url = "mysql+mysqldb://3ckRHqDbEegrMBt.root:l3GviezaL6VoMGIE@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/test?ssl_mode=VERIFY_IDENTITY&ssl_ca=<CA_PATH>"

Engine = create_engine(
    Database_url,
    pool_pre_ping=True,
    connect_args={
        "ssl" :{
            "ssl":True,
        }
    }
)

SessionLocal = sessionmaker(bind=Engine)

Base = declarative_base()