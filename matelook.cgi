#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2016
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/matelook/

use CGI qw/:all/;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;


sub main() {
    # print start of HTML ASAP to assist debugging if there is an error in the script
    print page_header();
    
    # Now tell CGI::Carp to embed any warning in HTML
    warningsToBrowser(1);
    $username = param('username') || '';
    $password = param('password') || '';
    # define some global variables
    $debug = 1;
    $users_dir = "dataset-medium";
    store_user_password();
    user_login();
    print page_trailer();
}


#
# Show unformatted details for user "n".
# Increment parameter n and store it as a hidden variable
#
sub user_page {
    my $n = param('n') || 0;
    #@users = sort(glob("$users_dir/*"));
    $user_to_show  = "$users_dir/$username";
    my $details_filename = glob("$user_to_show/user.txt");
    open my $p, "$details_filename" or die "can not open $details_filename: $!";
    $details = join '', <$p>;

    #my added code
    my $image = "$user_to_show/profile.jpg";
    my $details = hide_privacy($details);
    my $content = print_posts();
    close $p;
    my $next_user = $n + 1;


print <<eof
<ul>
eof
;

#print the mate list, links to their user page not implemented
foreach $key(keys %mate_list){
print <<eof
<li><a href>$mate_list{$key}</a></li>
eof
;
}

print <<eof
<\ul>
eof
;

#print user's info and their posts in reverse chronological order  
    return <<eof
</div>
<img src= "$image"alt=""/>
<div class="matelook_user_details">
$details
</div>
<div class="matelook_user_posts">
<p id="content_box">$content</p>
</div>
<p>
<form method="POST" action="">
    
    <input type="submit" name="Log out" value="Log out" class="matelook_button">
</form>
eof
}


#
# HTML placed at the top of every page
#
sub page_header {
    return <<eof
Content-Type: text/html;charset=utf-8

<!DOCTYPE html>
<html lang="en">
<head>
<title>matelook</title>
<link href="matelook.css" rel="stylesheet">
</head>
<body>
<div class="matelook_heading">
matelook
</div>
eof
}


#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}

#store users' passwords into hash
sub store_user_password{
    my @ids = sort(glob("$users_dir/*"));
    %user_password=();
    foreach $id(@ids){
        my $filename = "$id/user.txt";
        open my $file, "$filename" or die "$id: $!";
        $details = join '', <$file>;
        $id =~ s/dataset.*\///;
        if ($details =~ /password\=(\w+)\n/){
            $user_password{$id} = $1;
        }
        close $file;
    }
}

#creates a hash to store user's mates' zid and names
sub store_mate_list{
    %mate_list=();
    my $users = glob("$users_dir");
    my $user = "$users/$username";
    my $file_mates = "$user/user.txt";
    open my $file, "$file_mates" or die "$file_mates: $!";
    my $details = join '', <$file>;
    close $file;
    if ($details =~ /mates\=(.*)\n/){
        my $mates_string = $1;
        $mates_string =~ s/mates\=//; #regex to remove extract zid from
        $mates_string =~ s/\[//;      #the mates list
        $mates_string =~ s/\]//;
        my @mates = split(/,/, $mates_string); 
        foreach my $mate(@mates){
            $mate =~ s/\s//g;
            my $mate_file = "$users/$mate/user.txt";
            open my $F, "$mate_file" or die "$mate_file: $!";
            my $s = join '', <$F>;
            if ($s =~ /full\_name\=(.+)\n/){ #regex to locate the full name
                $mate_list{$mate} = $1;      #in the line containing it
            }
            close $F;
        }   
    }
}

#uses code from lab to implement user authentication
#if enter username and password correct then redirect to user's page
sub user_login{
    if ($username && $password) {
        if (exists($user_password{$username})){
            $correct_password = $user_password{$username};
            $password =~ s/[^a-zA-Z0-9]*//g;
            if ($password eq $correct_password){
                store_mate_list();
                print user_page();
            } else {
                print "Incorrect password!\n";
            }
        }else{
            print "Unknown username!\n";
        }
    } elsif ($username && !$password){
        print start_form, "\n";
        print "Password:\n", textfield('password'), "\n";
        print submit(value => Login), "\n";
        print hidden('username' => $username);
        print end_form, "\n";
    } elsif (!$username && $password){  
        print start_form, "\n";
        print "Username:\n", textfield('username'), "\n";
        print submit(value => Login), "\n";
        print hidden('password' => $password);
        print end_form, "\n";
    } else {
        print start_form, "\n";
        print "Username:\n", textfield('username'), "\n";
        print "Password:\n", textfield('password'), "\n";
        print submit(value => Login), "\n";
        print end_form, "\n";
    }
}

#hide private information such as email, password, etc in user profile
sub hide_privacy {
    $modified = shift(@_);
    $modified =~ s/password\=\w+\n//;
    $modified =~ s/email\=.*\n?//;
    $modified =~ s/home_suburb\=.*\n?//;
    $modified =~ s/home_latitude\=.*\n?//;
    $modified =~ s/home_longitude\=.*\n?//;
    $modified =~ s/courses\=.*\n?//;
    $modified =~ s/mates\=.*\n?//;
    return $modified;
}

#this subroutine creates a string of user's post in reverse chronological order
#and returns the string to the main function to be added to the html tag as $content
sub print_posts {
    my $post_list;
    my @posts = reverse(glob("$user_to_show/posts/*"));
    foreach my $post(@posts){
        open my $file, "$post/post.txt" or die "can not open $post: $!";
        $details = join '', <$file>;
        $post_list = $post_list.$details;
        $post_list = $post_list."\n";
    }
    return $post_list;
}
main();
