hotels_simple=[
    'Room Was Acceptable',
    'The room was nice',
    'the furnishings were comfortable.',
    'The food from the restaurant was very good',
    'Staff was very pleasant',
    'Staff was very helpful',
    'I had excellent shuttle service.',
    'The rooms are lovely',
    'the food was good hearty',
    'Our stay at this hotel was wonderful.',
    'The staff was very courteous upon check-in',
    'Our room was perfectly spotless.'
    'The Sports Bar had good food with very reasonable prices.'
]

hotels_simple_tagged = [
    [('room', 'NP'), ('was', 'VP'), ('acceptable', 'ADJP')],
    [('the room', 'NP'), ('was', 'VP'), ('nice', 'ADJP')],
    [('the furnishings', 'NP'), ('were', 'VP'), ('comfortable', 'ADJP')],
    [('the food', 'NP'), ('from the restaurant', 'PP'), ('was', 'VP'), ('very good', 'ADJP')],
    [('staff', 'NP'), ('was', 'VP'), ('very pleasant', 'ADJP')],
    [('staff', 'NP'), ('was', 'VP'), ('very helpful', 'ADJP')],
    [('i', 'PRP'), ('had', 'VP'), ('excellent', 'ADJP'), ('shuttle service', 'NP')],
    [('the rooms', 'NP'), ('are', 'VP'), ('lovely', 'ADJP')],
    [('the food', 'NP'), ('was', 'VP'), ('good', 'ADJP'), ('hearty', 'NN')],
    [('Our stay', 'NP'), ('at this hotel', 'PP'), ('was', 'VP'), ('wonderful', 'ADJP')],
    [('The staff', 'NP'), ('was', 'VP'), ('very courteous', 'ADJP'), ('upon check-in', 'PP')],
    [('Our room', 'NP'), ('was', 'VP'), ('perfectly spotless', 'ADJP')],
    [('The Sports Bar', 'NP'), ('had', 'VP')]
]

hotels_compound = [
    'The room was nice and the furnishings were comfortable.',
    'Staff was very pleasant and helpful',
    'Check in was fast and courteous',
    'Rooms were clean, spacious and comforatable.',
    'Big pool area, very good fitness center - nice lobby and common areas.',
    'The staff was friendly and helpful, they upgraded our room to queen beds without us asking.',
    'Rooms are large but very plain',
    'Room was cool, clean and comfy.',
    'The food and service was outstanding',
    'Staff was courteous and efficient',
    'The staff was extremely helpful and friendly.',
    'I really liked the hotel, it was very clean, the staff were fantastic and the rooms were great.'
]

hotels_complex = [
    'Bathroom sink was on a slight slant because it was pulling out of the wall.',
    'Though the bathrooms are a bit old, the beds are still cozy.',
    'I would say they are the best part of the hotel!',
    'There was construction being done on the street in front of the hotel; which made it very difficult driving around.'
]

hotels_compound_complex = [
    'I was there 3 nights for a conference and am giving it 5 stars, as it was quite reasonably priced for what we received.',
]

hotels_implicit_aspect = [
    'Very clean and well maintained.',
    'I would absolutely stay here again'
]

categories = [
    'COMFORT',
    'QUALITY',
    'PRICES',
    'CLEANLINESS',
    'DESIGN_FEATURES',
]




