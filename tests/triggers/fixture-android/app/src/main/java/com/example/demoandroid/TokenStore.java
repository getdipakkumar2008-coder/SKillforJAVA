package com.example.demoandroid;

import android.content.Context;
import android.content.SharedPreferences;

public class TokenStore {

    private final SharedPreferences prefs;

    public TokenStore(Context context) {
        this.prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
    }

    public void save(String accessToken) {
        prefs.edit().putString("access_token", accessToken).apply();
    }

    public String load() {
        return prefs.getString("access_token", null);
    }
}
