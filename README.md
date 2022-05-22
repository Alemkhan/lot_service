# Sample API requests

## Create Lot request body
```http request
POST localhost:8000/api/lot
```
"payment" field is a list of payment ids that related to user:

to get user's payment data which includes (id, bank_name, requisite_number, payment_type)
see the Get Payment block below

```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWxlbUBnbWFpbC5jb20iLCJleHBpcmVzIjoxNjUyODkyODU2LjM5NTA2NX0.6umWJmxIMLQJEfbhOkA9IT0RQKeWXq3vCVwH1Ka1Hx0",
    "price": 1000,
    "supply": 12,
    "min_limit": 1,
    "max_limit": 12,
    "lot_type": "sell",
    "currency": "eth",
    "payment": [1, 2]
}
```
## Get, Delete Lot request body
```http request
GET DELETE localhost:8000/api/lot/detail
```
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWxlbUBnbWFpbC5jb20iLCJleHBpcmVzIjoxNjUyODkyODU2LjM5NTA2NX0.6umWJmxIMLQJEfbhOkA9IT0RQKeWXq3vCVwH1Ka1Hx0"
}
```

##Get all lots
```http request
GET localhost:8000/api/lot
```

## Get Payment
### This api returns list of payment data related to user email, and can delete all payment data
```http request
GET DELETE localhost:8000/api/payment/detail
```
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWxlbUBnbWFpbC5jb20iLCJleHBpcmVzIjoxNjUyODkyODU2LjM5NTA2NX0.6umWJmxIMLQJEfbhOkA9IT0RQKeWXq3vCVwH1Ka1Hx0"
}
```

##Get all payment data
```http request
GET localhost:8000/api/payment
```
