from decimal import Decimal
import copy

class POS:
  def __init__(self, ccy='gbp', ref_start=1):
    self.ccy          = ccy
    self.ref          = ref_start
    self.bill_list    = {}
    self.system_total = Decimal(0)

  def new_bill(self):
    self.ref += 1
    return Bill(self, self.ref)

  def new_item(self, name, price, discount=None, tax=0, tags=[], price_include_vat=True):
    return Item(self.ccy, name, price, discount, tax, tags, price_include_vat)

  def submit(self, bill):
    self.system_total += bill.subtotal
    bill_ref           - bill.bill_ref

    if bill_ref in self.bill_ref.keys():
      print('Bill {} has already been submitted!'.format(bill_ref))
    else:
      self.bill_list[bill_ref] = bill

class Bill:
  def __init__(self, pos, bill_ref):
    # Amounts will remain in cents until gotten
    self.pos       = pos
    self.subtotal  = Decimal(0)
    self.tax       = Decimal(0)
    self.discount  = Decimal(0)
    self.bill_ref  = bill_ref
    self.items     = {}
    self.submitted = False

  def add_item(self, item, qty=1):
    '''
    Add an item object to a bill.
    Takes arguments...
    - item (A valid item object)
    - qty  (Optional, defaults to 1)
    '''
    if not self.submitted:
      item = copy.deepcopy(item)

      for _ in range(qty):
        if item.name in self.items.keys():
          self.items[item.name][1] += 1
        else:
          self.items[item.name] = [item, 1]

      self.retotal()

  def reset(self):
    '''
    Removes all items from the bill and zeroes balances
    '''
    if not self.submitted:
      self.items.clear()
      self.retotal()

  def retotal(self):
    '''
    Calculates the bill balances by iterating over the items.
    '''
    self.subtotal = Decimal(0)
    self.tax      = Decimal(0)
    self.discount = Decimal(0)

    for key, item in self.items.items():
      qty, item = item[1], item[0]
      price     = item.price
      tax       = item.tax
      # Remove any VAT
      if item.price_include_vat:
        price = (price * 100) // (tax + 100)
      #Check whether a discount is to be applied
      dscnt = discounter(item.discount, qty, price)
      #Total up
      price = (price * qty) - dscnt
      tax   = (price // Decimal(100) * tax)

      self.discount += dscnt
      self.tax      += tax
      self.subtotal += (price + tax)

  def discounter(discount, quantity, i_price):
    '''
    Calculates the discounted amount in cents for a given item, and
    returns it as a Decimal object.

    Arguments
    - discount
    - quantity
    - price
    '''
    if not discount:
      return Decimal(0)

    d_amount = d_qty = 0

    if discount and discount[2] == 0 and (discount[0] + discount[1]) <= quantity:
      #Quantity Discount
      tot      = discount[0] + discount[1]
      d_qty    = quantity // tot
      d_amount = i_price
    elif discount and discount[2] == 1 and discount[0] <= quantity:
      #Monetary Discount
      d_qty    = quantity // discount[0]
      d_amount = Decimal(discount[1])

    return Decimal(d_amount * d_qty).quantize(0, rounding='ROUND_DOWN')

  def submit():
    if self.submitted:
      print("This bill has already been submitted.")
    else:
      self.retotal()
      self.submitted = True
      self.pos.submit(copy.deepcopy(self))

class Item:
  def __init__(self, ccy, name, price, discount, tax, tags, price_include_vat):
    '''
    Items are created through the POS object, and added to bill objects
    ccy      - The systems currency
    name     - Must be a string
    price    - Must be an integer representing the price in its smallest unit.
    discount - Must be nil or an array with three values
                 - The first value  (x) is the quantity required to trigger the discount
                 - The second value (y) is the discount to be applied (Integer)
                 - The third value is either - 0 - Buy x get y free (y is a quantity)
                                             - 1 - Buy x get y off  (y is an amount in pence)
    tax      - Must be an integer representing the tax in its smallest unit.
    tags     - Must be a string or array of strings
    '''
    self.ccy   = ccy
    self.name  = name
    self.price = Decimal(int(price))
    self.tax   = Decimal(int(tax))
    self.tags  = tags
    self.price_include_vat = price_include_vat

    if self.check_discount(discount):
      self.discount = discount
    else:
      self.discount = None

  ## DISCOUNT GETTER, SETTER, and CHECKER
  @property
  def discount(self):
    return self.__discount

  @discount.setter
  def discount(self, discount):
    if self.check_discount(discount):
      self.__discount = discount
    else:
      print('Invalid value for discount.')

  @discount.getter
  def discount(self):
    return self.__discount

  @property
  def tags(self):
    self.__tags

  @tags.setter
  def tags(self, tags):
    if type(tags) is list:
      self.__tags = tags
    else:
      print('Invalid value for tags.')

  @tags.getter
  def tags(self):
    return self.__tags

  @property
  def price_include_vat(self):
    self.__price_include_vat

  @price_include_vat.setter
  def price_include_vat(self, price_include_vat):
    if type(price_include_vat) is bool:
      self.__price_include_vat = price_include_vat
    else:
      print('Invalid value for VAT flag.')

  @price_include_vat.getter
  def price_include_vat(self):
    return self.__price_include_vat

  def check_discount(self, discount):
    if ((discount is None)       or
       (type(discount) is list   and
        len(discount) == 3       and
        type(discount[0]) is int and
        type(discount[1]) is int and
        type(discount[2]) is int and
        0 <= discount[2] <= 1)):
      return True
    return False
