<?php
// Safe counterpart to vulnerable.php.
// The policy binds the row to the caller. Validation is the field allowlist.

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;

class UserController extends Controller
{
    public function update(Request $request, User $user)
    {
        $this->authorize('update', $user);

        $data = $request->validate([
            'name' => ['required', 'string', 'max:100'],
            'email' => ['required', 'email'],
        ]);
        $user->update($data);

        return response()->json($user->only(['id', 'name', 'email']));
    }
}
