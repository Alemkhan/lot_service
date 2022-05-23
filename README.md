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

Response body
```json
{
    "success": "true",
    "status code": 200,
    "message": "Lot fetched successfully",
    "data": {
        "lot": {
            "id": 1,
            "payment": [
                {
                    "id": 1,
                    "seller_id": "alem@gmail.com",
                    "bank_name": "kaspi",
                    "requisite_number": "87079209311",
                    "payment_type": "phone"
                },
                {
                    "id": 2,
                    "seller_id": "alem@gmail.com",
                    "bank_name": "halyk",
                    "requisite_number": "1111 2222 3333 4444",
                    "payment_type": "bank_number"
                }
            ],
            "seller_id": "alem@gmail.com",
            "price": 100.0,
            "supply": 0.0,
            "min_limit": 0.0,
            "max_limit": 0.0,
            "lot_type": "sell",
            "currency": "kzt"
        },
        "wallet": {
            "id": "62851355a83ea8fad65a9103",
            "address": "0x14254a4a97bf67DEC1bA6240c9446003d250ae2b",
            "balance": 0
        }
    }
}
```

##Get all lots
```http request
GET localhost:8000/api/lot
```
Response model
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "payment": [
                {
                    "id": 1,
                    "seller_id": "alem@gmail.com",
                    "bank_name": "kaspi",
                    "requisite_number": "87079209311",
                    "payment_type": "phone"
                },
                {
                    "id": 2,
                    "seller_id": "alem@gmail.com",
                    "bank_name": "halyk",
                    "requisite_number": "1111 2222 3333 4444",
                    "payment_type": "bank_number"
                }
            ],
            "seller_id": "alem@gmail.com",
            "price": 100.0,
            "supply": 0.0,
            "min_limit": 0.0,
            "max_limit": 0.0,
            "lot_type": "sell",
            "currency": "kzt"
        },
        {
            "id": 2,
            "payment": [
                {
                    "id": 4,
                    "seller_id": "sungat@mail.ru",
                    "bank_name": "jysan",
                    "requisite_number": "2222 3333 4444 5555",
                    "payment_type": "bank_number"
                }
            ],
            "seller_id": "sungat@mail.ru",
            "price": 300.0,
            "supply": 10.0,
            "min_limit": 0.0,
            "max_limit": 10.0,
            "lot_type": "buy",
            "currency": "kzt"
        }
    ]
}
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

Response model
```json
{
    "success": "true",
    "status code": 200,
    "message": "Payment requisites fetched successfully",
    "data": {
        "payment": [
            {
                "id": 1,
                "seller_id": "alem@gmail.com",
                "bank_name": "kaspi",
                "requisite_number": "87079209311",
                "payment_type": "phone"
            },
            {
                "id": 2,
                "seller_id": "alem@gmail.com",
                "bank_name": "halyk",
                "requisite_number": "1111 2222 3333 4444",
                "payment_type": "bank_number"
            }
        ]
    }
}
```

##Get all payment data
```http request
GET localhost:8000/api/payment
```

## Create payment data
```http request
POST localhost:8000/api/payment
```
```json
{
    "access_token": "",
    "bank_name": "",
    "requisite_number": "",
    "payment_type": "phone"
}
```
payment_types = ["phone", "bank_number"]
