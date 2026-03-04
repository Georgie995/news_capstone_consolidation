from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """User creation form bound to the CustomUser model with role selection.

    This ensures that registration creates instances of our custom user
    (with the additional role and subscription fields) instead of the
    default auth.User model.

    As per the capstone specification and marker feedback, new users must be
    able to choose a role (Reader, Editor, or Journalist) during sign‑up so
    that they can immediately access the features intended for that role.
    """

    # Expose the role as an explicit choice field backed by the model's
    # TextChoices. This guarantees that the form stays in sync with any
    # future changes to the Roles enum on CustomUser.
    role = forms.ChoiceField(
        choices=CustomUser.Roles.choices,
        help_text="Select your role so the correct permissions can be applied.",
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Password fields are provided by UserCreationForm itself.
        fields = ("username", "email", "role")

    def save(self, commit: bool = True) -> CustomUser:
        """Create the user, set the role, and attach the correct group.

        1. Save the base user instance (username, email, password).
        2. Apply the selected role to the CustomUser instance.
        3. Add the user to the corresponding Django auth Group:
           - Reader     -> "Reader"
           - Editor     -> "Editor"
           - Journalist -> "Journalist"

        Group membership is what actually grants the CRUD permissions on
        Article and Newsletter, so doing this here ensures that from the
        moment the account is created, the user has the appropriate access.
        """
        user: CustomUser = super().save(commit=False)

        # Apply the selected role from the form.
        selected_role = self.cleaned_data.get("role")
        if selected_role:
            user.role = selected_role

        if commit:
            user.save()
            # Once the user exists in the database, enforce any role/subscription
            # rules that rely on many-to-many relations and a primary key.
            user.enforce_role_subscription_rules()
            # After that, attach the user to the appropriate group based on
            # their role. If the group does not exist yet (e.g. migrations
            # not run), we fail silently.
            self._assign_group_for_role(user)

        return user

    def _assign_group_for_role(self, user: CustomUser) -> None:
        """Internal helper to attach the user to the correct Group.

        This complements the post_migrate signal that creates the
        "Reader", "Editor" and "Journalist" groups with the right
        permissions. By calling it here, new users are placed into the
        correct group as soon as they register.
        """
        role_to_group = {
            CustomUser.Roles.READER: "Reader",
            CustomUser.Roles.EDITOR: "Editor",
            CustomUser.Roles.JOURNALIST: "Journalist",
        }

        group_name = role_to_group.get(user.role)
        if not group_name:
            return

        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            # If the groups have not been created yet, we avoid raising an
            # exception during registration; the user can be added later.
            return

        user.groups.add(group)
