export type Admin = {
    id: number
    firstName: string | null
    phoneNumber: string
}

export type AdminLoginData = {
    phoneNumber: string
    password: string
}

export type AdminFetchResponse = {
    token: string
    user: Admin
}

export type User = {
    id?: number
    first_name: string | null
    last_name: string | null
    phone_number: string
    role: string | null
    categories: number[]
    car_number: string | null
    password?: string
}

export type UserFetchResponse = {
    count: number
    next: string | null
    previous: string | null
    results: User[]
}
