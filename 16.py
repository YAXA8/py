def tdef(reshte):
    en = 0
    rgh = 0
    fasl = 0
    sayer = 0

    for i in reshte:
        if i.isalpha():
            en += 1
        elif i.isdigit():
            rgh += 1
        elif i == " ":
            fasl += 1
        else:
            sayer += 1

    print(f"تعداد حروف: {en}")
    print(f"تعداد اعداد: {rgh}")
    print(f"تعداد فاصله ها: {fasl}")
    print(f"تعداد سایر کاراکتر ها: {sayer}")

tdef("hello 1234 !@#")
