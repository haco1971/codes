#!/usr/bin/perl -w
 ;#
 ;# ---------------------------
 ;#  ween, Perl IRC Bot (v .91)
 ;# ---------------------------
 ;#         (c) 2001 s0ttle.net
 ;###
 ;# 
 ;# 
 ;# Author: s0ttle (s0ttle@n2.com) 
 ;# 
 ;####
   ;#
   ;## ---------------------------------------------------
    ;# LEGAL NOTICE: This script may be freely copied,
    ;# distributed and modified. Use of the script is
    ;# at the risk of the user. The script is presented
    ;# "as-is" without any warranty, and the author is
    ;# not liable for any loss or damages arising out of
    ;# the use of or failure to use this script. This notice
    ;# must appear in any modified copy of the script in which
    ;# the name of the original author also appears.
   ;## ---------------------------------------------------
   ;# 
;#######

use Socket;
use strict;
use diagnostics; # Remove after release
use Getopt::Std;

#
;# config variables
#
my %switch;

my $bnick = 'ween';
my $bchan = '#perl';
my $fstamp = &ctime('f');
my $dstamp = &ctime('d');
my $ween = $0;
my $log = 0;
my $debug = 1;
my $config;
my $buffer;
my $server = 'irc2.nl.smashthestack.org';

$SIG{HUP} = \&hsignal;
$SIG{INT} = \&isignal;
########################
###
#


sub hsignal{

   my $signal = shift;
   &snd("QUIT :recieved-signal($signal), restarting");
   exec("perl $ween");
}


sub isignal{

   my $signal = shift;
   &snd("QUIT :recieved-signal($signal), bye...");
   exit(0);
}

getopts("c:f:s:di", \%switch);

			# 
			# -c [  channel  ]
			# -f [  config   ]
			# -s [  server   ]
			# -d [  debug    ]
			# -l [  logging  ]
			#

&opts(\%switch) if (%switch);

sub opts{
    
    my $switch = @_;

    if ($switch{s}) { $server = $switch{s}; }
    if ($switch{f}) { $config = $switch{f}; }
    if ($switch{c}) { $bchan  = $switch{c}; }
    if ($switch{d}) { $debug  = 1;          }
    if ($switch{i}) { $log    = 1;          }

    return;
}


&splash;
&init($server,6667);
&register;

sub init{

    my ($server,$port) = @_;
    my ($iaddr,$paddr,$proto);
 
    $iaddr = inet_aton($server) or die "Unable to resolve $server: $!\n";
    $paddr = sockaddr_in($port,$iaddr);
    $proto = getprotobyname('tcp');

    socket(SOCK, PF_INET, SOCK_STREAM, $proto) or die "Could not create socket: $!\n";

    if (connect(SOCK,$paddr)){
       print "/  [ $dstamp ] \n";
       print "/  Connected: $server->$port \n";

    } else { 
           die "Unable to connect to $server: $!\n";
    }

    select(SOCK); ++$|; select(STDOUT); ++$|;
    
    return;
}


sub rfsock{
   
    my $bytes = 2048;

    if (sysread(SOCK, $buffer, $bytes)){
       print "$buffer" if $debug == 1;

    } else { return; }
}


sub snd{

    my ($cmds) = @_;

    print "CMD: $cmds\n" if $debug == 1;
    return if print SOCK $cmds, "\x0A\x0D";
    die "Unable to write to socket: $!\n";
}


sub sndpong{
   
    my ($ping,$parg);

    if ($buffer=~/(PING[ ]+:[^ ]+)/i){ $buffer = $1;
       ($ping,$parg) = split(/ /,$buffer,2);
       substr($ping,1,1)='O';

       return if &snd("$ping $parg");
    }
}


sub splash{

    print "\n\n";
    print "/  ---------------------------\n";
    print "/  ween, Perl IRC Bot (v .91) \n";
    print "/  ---------------------------\n";
    print "/          (c) 2001 s0ttle.net\n";
    print "/  \n" x 2;

    return if sleep(2);
}


sub register{

    my $rbnick = 1;
    my $buser = 'ween';
    my $bpasswd = 'eew33n';
    
    print "/\n/  Registering.....      \n";
    print "/\n" x 2, "/  ---------------------------\n";
    sleep(2);

    &snd("USER $buser buf buf :$bnick v .91");
   
    while (1){
        print "1 WHILE\n";
        &rfsock;
        &snd("NICK $bnick");

        if ($buffer=~/ 433 /){
           substr($bnick,1,2)='33';
        }
 			#
			# 431 ERR_NONICKNAMEGIVEN
			# 432 ERR_ERRONEUSNICKNAME
			# 433 ERR_NICKNAMEINUSE
			#

        last if ($buffer=~/ 376 /);    # eNd MOTD
        &sndpong if ($buffer=~/PING/);

        die $!, "\n" if $buffer=~/ :Closing Link: /;   # could recall init()
    }

    if ($rbnick == 1 && $bnick eq 'ween'){
       &snd("PRIVMSG NickServ :identify $bpasswd"); # 451 ERR_NOTREGISTERED
       &rfsock;
       &jchan;

    } else {
           &rfsock;
           &jchan;
    }
}


sub jchan{

    my $reason;
    
    &snd("JOIN $bchan");

    while(1){
        &rfsock;
      
        if ($buffer=~/ (47(?:1|3|4|5)) /){

			#
			# 471 ERR_CHANNELISFULL
			# 473 ERR_INVITEONLYCHAN
			# 474 ERR_BANNEDFROMCHAN
			# 475 ERR_BADCHANNELKEY
			#

           $reason = $1; 
           last if print "Could not join $bchan: $reason\n";

        }

        if ($buffer=~/ 366 /){    # End Names List
           last if print "Now on $bchan\n";     
        }
    }

    return if &gusers;
}


sub gusers{

#
# Nothing really done with this
# function, but the there are some 
# foreseeable uses.
#

    my (
         %user,@who,$wholist,$status,
         $misc,$ident,$host,$nick,$users
       );
   
    &snd("WHO $bchan");
   
    while (1){
        print "2 WHILE\n" if $debug == 1;
        &rfsock;
        $wholist .= $buffer;
        last if ($buffer=~/ 315 /); # End of /who list
    }  

    @who = split(/\n/,$wholist);
    $users = 0;

    foreach(@who){ 
        if (/ 352 /){
           ($ident,
            $host,
            $nick,
            $status,
            $misc) = (/ 352 [^ ]+ [^ ]+ ([^ ]+) ([^ ]+) [^ ]+ ([^ ]+) ([^ ]+) :\d (.*)/);
            $user{$nick} = $host; print "$ident,$host,$nick,$status,$misc\n";
            $users++;        
        }
    }

    return if print "$users user(s) on $bchan\n";
}


sub gmanp{

    my ($nick,$cmd) = @_;
    my ($manpage,$synopsis,$description);
   
    if ($cmd=~/[^\w.]+/){
       &snd("NOTICE $nick :hehe, nice try!\n");

    } else { 
   
             # man cmd | col -b  
             open (MAN, "/usr/bin/man $cmd | ul -t dumb |")
                  || die "Cannot run command 'man': $!\n";
    
             $manpage = join('', <MAN>);

             if ($manpage =~ /^SYNOPSIS(.*?)\n\n/ms){
                $synopsis = $1;
             }
 
             if ($manpage =~ /^DESCRIPTION(.*?)\n\n/ms){
                $description = $1;
             }
   
             if ($synopsis && $description){
                $synopsis =~s/^\s+//;
                $synopsis =~s/\s{2,}/ /g;
   
                $description =~s/^\s+//;
                $description =~s/\s{2,}/ /g;

                &snd("NOTICE $nick :$synopsis");
                &snd("NOTICE $nick :$description");

             } else {
                    &snd("NOTICE $nick :No manual entry for $cmd");
             }

             return if close(MAN);
    }
}


sub gpdoc{

    my ($nick,$args) = @_;

    &snd("NOTICE $nick :comming soon!");
}


sub ctcp{

    my $version = "[\cbween\cb] IRC \cbperl\cb-bot v .91";
    my ($nick,$ctcp) = @_;

    if ($ctcp=~/VERSION/){
       &snd("NOTICE $nick :$version, by s\cb0\cbttle");  
    }
   
    elsif ($ctcp=~/PING/){
          &snd("NOTICE $nick :\cbPONG\cb!");
    }
}


sub ctime{

#
# use POSIX qw/strftime/;
# 
# I wanted to do it without the 
# module edit it out if you want
# and do it yourself.
#

    my ($stamp) = @_;
    my (
         %months,%time,@days,
         $end,$mname,$tstamp,$t
       );

    %months = (
                Jan => '01', Jul => '07',
                Feb => '02', Aug => '08',
                Mar => '03', Sep => '09',
                Apr => '04', Oct => '10',
                May => '05', Nov => '11',
                Jun => '06', Dec => '12'
              );                   

    @days = (
              'Sun', 'Mon',
              'Tue', 'Wed',
              'Thu', 'Fri',
              'Sat'
            );
 
    ( $time{sec},$time{min},
      $time{hour},$time{day},
      $time{month},$time{year},$time{day2} ) = (localtime(time))[0,1,2,3,4,5,6];
   
    foreach $t (sort(keys(%time))){
       next if ($t=~/year|day2/);

       if ($time{$t} < 10){
          $time{$t} = 0 . $time{$t};
       }
    }

    $time{year} += "1900";
   
    if ($time{hour} >= 12) {
       $end = "PM";

    } else { $end = "AM"; }

    if ($time{hour} == 0) { $time{hour} = 12; }
    if ($time{hour} > 12) { $time{hour} -= 12; }

    if ($stamp eq 'd'){
       %months = reverse(%months);

			#
			# keep from doing '01' => 'Jan'
			# if you want to you can edit
			# it out :p
			#
			
       $mname  = $months{++($time{month})};
   
       $tstamp .= "$days[$time{day2}], ";
       $tstamp .= "$time{day} $mname "; 
       $tstamp .= "$time{year} ";
       $tstamp .= "($time{hour}:$time{min}:$time{sec} $end)";
     
       return ("$tstamp");
    } 

    elsif ($stamp eq 'f'){
          ++($time{month});

          return ("$time{month}-$time{day}-$time{year}");
    }
}


sub cmdCheck{

    my $args;
    my ($nick,$cmd) = @_;

    if ($cmd=~/^ween: ([a-z]+);/){ 
       $cmd = $1;
       &cmdtasker($nick,$cmd);
    }

    elsif ($cmd=~/^ween: ([a-z]+) ([^ ]+);/){
          ($cmd,$args) = ($1,$2);
           &cmdtasker($nick,$cmd,$args); }

    elsif ($cmd=~/^ween: ([a-z]+) ([^ ]+ [^ ]+);/){
          ($cmd,$args) = ($1,$2);
          &cmdtasker($nick,$cmd,$args); }

    elsif ($cmd=~/^ween: ([a-z]+) ([^ ]+ [^ ]+ [^ ]+);/){
          ($cmd,$args) = ($1,$2);
          &cmdtasker($nick,$cmd,$args); }

    elsif ($cmd=~/^ween: perldoc -f ([\w:]+);/){
          ($cmd,$args) = ("perldoc",$1);
          &cmdtasker($nick,$cmd,$args);
 
    } else {
           &snd("NOTICE $nick :Check Syntax or, ween: help;");
    }
}


sub cmdtasker{

    my ($nick,$cmd,$args) = @_;

    if ($cmd=~/man/){
          &gmanp($nick,$args);
    }

    elsif ($cmd=~/perldoc/){
          &gpdoc($nick,$args); 

    } else {
           &snd("NOTICE $nick :Command not found or implemented!");
    }
}


sub lparse{

    my $ctcp;
    my ( $nick,
         $ident,
         $host,
         $action,
         $who,
         $text ) = ($buffer=~/:([^!]+)!([^@]+)@([^ ]+)\s([^ ]+)\s([^ ]+)\s:(.*)/);
         $text=~s/\cb//g; $text=~s/\ca//g;
   
    print "<$nick> $text\n" if $debug == 0;
     
    if ($text=~/^ween:/){
       &cmdCheck($nick,$text);
       print "<$nick> $text\n" if $debug == 0;
    }
    
    if ($text=~/VERSION|PING/){
       $ctcp = $text;
       &ctcp($nick,$ctcp);
    } 
   
} 


sub mparse{

    my ($anick,
        $action,
        $nick,
        $text ) = ($buffer=~/:([^!]+)![^ ]+ ([^ ]+) $bchan ([^ ]+) :(.*)/);
        print "$anick-$action-$nick-$text\n"; 
    
    if (($action=~/KICK/) && $nick eq $bnick){
       &snd("JOIN $bchan");
    }
}
     



sub nparse{

    my ( $anick,
         $flag,
         $nick ) = ($buffer=~/:([^!]+)![^ ]+ MODE $bchan ([-ovkb+]+) (.*)/);
         return if print "*** $anick $flag $nick\n";
}
   

 
;##########
;##########
;##########
;#        #
;#  main  #  

;################

while(1){ 

   print "MAIN LOOP\n" if $debug == 1;
   &rfsock;
  
   if ($buffer=~/PING/){
      &sndpong;
   }

   if ($buffer=~/:[^!]+![^@]+@[^ ]+ [^ ]+ [^ ]+ :.*/){
      &lparse;
   }

   if ($buffer=~/:[^!]+![^ ]+ [^ ]+ $bchan [^ ]+ :.*/){
      &mparse;
   }

   if ($buffer=~/(:[^!]+![^ ]+ MODE $bchan [-ovkb+]+ .*)/){ 
      &nparse;
   }

}


;#
;# eNd
;#         

