from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

from database_setup import Category, Base, CategoryItem, User

engine = create_engine('sqlite:///categories.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user1 = User(name="Primary User", email="primaryUser@gmail.com")

# items for handTools
category1 = Category(name="Hand Tools")

session.add(category1)
session.commit()

categoryItem1 = CategoryItem(name="Saw", description="A tool consisting of " +
                             "a tough blade, wire, or chain with a hard " +
                             "toothed edge. It is used to cut material" +
                             ", very often wood though sometimes metal or" +
                             " stone. The cut is made by placing the toothed" +
                             " edge against the material and moving it " +
                             "forcefully forth and less forcefully back " +
                             "or continuously forward.",
                             created_at=datetime.datetime.now(),
                             category=category1, user=user1)

session.add(categoryItem1)
session.commit()


categoryItem2 = CategoryItem(name="Hammer", description="A tool consists of" +
                             " a weighted 'head' fixed to a long handle that" +
                             " is swung to deliver an impact to a small area" +
                             " of an object. This can be, for example, " +
                             "to drive nails into wood, to shape metal or to" +
                             " crush rock.",
                             created_at=datetime.datetime.now(),
                             category=category1, user=user1)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name="File", description="A tool used to shape " +
                             "materials, by cutting away some of it. Today," +
                             " files are usually made of a steel bar that " +
                             "has a rough surface.",
                             created_at=datetime.datetime.now(),
                             category=category1, user=user1)

session.add(categoryItem3)
session.commit()

# items for powerTools
category2 = Category(name="Power Tools")

session.add(category2)
session.commit()

categoryItem1 = CategoryItem(name="Air Compresser", description="A device" +
                             "that converts power (using an electric motor," +
                             " diesel or gasoline engine, etc.) into " +
                             "potential energy stored in pressurized air." +
                             " By one of several methods, an air compressor" +
                             " forces more and more air into a storage tank," +
                             " increasing the pressure.",
                             created_at=datetime.datetime.now(),
                             category=category2, user=user1)

session.add(categoryItem1)
session.commit()


categoryItem2 = CategoryItem(name="Heat Gun", description="A device used to" +
                             " emit a stream of hot air, usually at" +
                             " temperatures between 100 C and 550 C" +
                             " (200-1000 F), with some hotter models running" +
                             " around 760 C (1400 F), which can be held" +
                             " by hand.", created_at=datetime.datetime.now(),
                             category=category2, user=user1)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name="Power Screwdriver",
                             description="A cordless power tool used to set " +
                             "or remove screws.",
                             created_at=datetime.datetime.now(),
                             category=category2, user=user1)

session.add(categoryItem3)
session.commit()

# items for outdoorTools
category3 = Category(name="Outdoor Tools")

session.add(category3)
session.commit()

categoryItem1 = CategoryItem(name="Shovel", description=" a tool for digging" +
                             " lifting, and moving bulk materials, such as" +
                             " soil, coal, gravel, snow, sand, or ore.",
                             created_at=datetime.datetime.now(),
                             category=category3, user=user1)

session.add(categoryItem1)
session.commit()


categoryItem2 = CategoryItem(name="Rakes", description="a broom for outside" +
                             " use; a horticultural implement consisting " +
                             "of a toothed bar fixed transversely to a " +
                             "handle, or tines fixed to a handle, and used " +
                             "to collect leaves, hay, grass, etc., and " +
                             "in gardening, for loosening the soil, light" +
                             " weeding and levelling, removing dead grass" +
                             " from lawns, and generally for purposes " +
                             "performed in agriculture by the harrow.",
                             created_at=datetime.datetime.now(),
                             category=category3, user=user1)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name="Hoe", description="an ancient and " +
                             "versatile agricultural and horticultural hand" +
                             " tool used to shape soil, remove weeds, " +
                             "clear soil, and harvest root crops. Shaping " +
                             "the soil includes piling soil around the base " +
                             "of plants (hilling), digging narrow furrows" +
                             " (drills) and shallow trenches for planting " +
                             "seeds or bulbs. Weeding with a hoe includes" +
                             " agitating the surface of the soil or cutting" +
                             " foliage from roots, and clearing soil of old" +
                             " roots and crop residues. Hoes for digging " +
                             "and moving soil are used to harvest root crops" +
                             " such as potatoes.",
                             created_at=datetime.datetime.now(),
                             category=category3,
                             user=user1)

session.add(categoryItem3)
session.commit()

# items for KitchenTools
category4 = Category(name="Kitchen Tools")

session.add(category4)
session.commit()

categoryItem1 = CategoryItem(name="Whisks", description="A cooking utensil" +
                             " that can be used to blend ingredients smooth " +
                             "or to incorporate air into a mixture, in a " +
                             "process known as whisking or whipping.",
                             created_at=datetime.datetime.now(),
                             category=category4, user=user1)

session.add(categoryItem1)
session.commit()


categoryItem2 = CategoryItem(name="Peeler", description="a kitchen tool" +
                             " consisting of a slotted metal blade attached " +
                             "to a handle that is used to remove the outer " +
                             "skin or peel of certain vegetables, often" +
                             " potatoes and carrots, and fruits such as " +
                             "apples, pears, etc.",
                             created_at=datetime.datetime.now(),
                             category=category4, user=user1)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name="Measuring Cup", description="A kitchen " +
                             "utensil used to measure the volume of" +
                             " liquid or solid cooking ingredients such " +
                             "as flour and sugar, especially for volumes" +
                             " from about 50 mL (2 fl oz) upwards.it is may" +
                             " be made of plastic, glass, or metal." +
                             " Transparent (or translucent) cups can be read" +
                             " from an external scale; metal ones only from" +
                             " a dipstick or scale marked on the inside. ",
                             created_at=datetime.datetime.now(),
                             category=category4, user=user1)

session.add(categoryItem3)
session.commit()

# items for ArchitectTools
category5 = Category(name="Architect Tools")

session.add(category5)
session.commit()

categoryItem1 = CategoryItem(name="Architect's Scale",
                             description="A specialized ruler designed to" +
                             " facilitate the drafting and measuring of " +
                             "architectural drawings, such as floor plans" +
                             " and orthographic projections.",
                             created_at=datetime.datetime.now(),
                             category=category5, user=user1)

session.add(categoryItem1)
session.commit()


categoryItem2 = CategoryItem(name="Technical Mechanical Pencil",
                             description="A mechanical pencil (US English)" +
                             " or propelling pencil (UK English), also" +
                             " clutch pencil, is a pencil with a" +
                             " replaceable and mechanically extendable" +
                             " solid pigment core called a 'lead'. The lead," +
                             " often made of graphite, is not bonded to the" +
                             " outer casing, and can be mechanically" +
                             " extended as its point is worn away.",
                             created_at=datetime.datetime.now(),
                             category=category5, user=user1)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name="Tracing Paper",
                             description="A paper made to have low opacity," +
                             " allowing light to pass through. It was" +
                             " originally developed for architects and " +
                             "design engineers to create drawings which " +
                             "could be copied precisely using the diazo " +
                             "copy process; it then found many other uses.",
                             created_at=datetime.datetime.now(),
                             category=category5, user=user1)

session.add(categoryItem3)
session.commit()

print "added categories items!"
